# Copyright (c) 2022, Offshore Evolution Pvt Ltd and contributors
# For license information, please see license.txt

import json
from frappe import _
import frappe
from frappe.model.document import Document
from six import string_types
from datetime import datetime 
import requests
from frappe.utils import add_to_date
from datetime import timedelta, date
from oxo.oxo.doctype.ts_whatsapp_settings.ts_whatsapp_settings import whatsapp
import urllib.parse

class DueDiligence(Document):
    pass

@frappe.whitelist()
def get_email_template_details(doctype, name, quotationName, source_doctype="Quotation"):
    
    quotationDoc = frappe.get_doc(source_doctype, quotationName)
    docAsDict = quotationDoc.as_dict()
    
    email_subject = frappe.db.get_value('Email Template', name, 'subject')
    email_body = frappe.db.get_value('Email Template', name, 'response')
    email_body = frappe.render_template(email_body, docAsDict)
    
    return [email_subject, email_body]

@frappe.whitelist()
def send_email_due_diligence(send_to, email_template, contact_person, quotation, source_doctype="Quotation"):
    
    newDocName = create_due_diligence(send_to, email_template, contact_person, quotation, source_doctype)
    
    quotationDoc = frappe.get_doc(source_doctype, quotation)
    docAsDict = quotationDoc.as_dict()
    
    email_subject = frappe.db.get_value('Email Template', email_template, 'subject')
    email_body = frappe.db.get_value('Email Template', email_template, 'response')
    email_body = frappe.render_template(email_body, docAsDict)
    email_body = email_body.replace("{{ due_diligence_secure_url }}", f"""<b>{source_doctype}: </b><a href="{frappe.utils.get_url()+f"/proposal?quotation={quotation}&doctype={source_doctype}"}">{quotation}</a>""")
    
    frappe.sendmail(
        recipients =  send_to,
        sender =  frappe.session.user,
        subject = email_subject,
        message = email_body,
        delayed = False,
        
    )

    url = frappe.utils.get_url()
    return [url, newDocName]

@frappe.whitelist()
def send_whatsapp_due_diligence(sales_partner, email_template, doctype, docname):
    newDocName = create_due_diligence(sales_partner, email_template, "", docname, doctype)
    
    Doc = frappe.get_doc(doctype, docname)
    docAsDict = Doc.as_dict()
    
    email_subject = frappe.db.get_value('Email Template', email_template, 'subject')
    email_body = frappe.db.get_value('Email Template', email_template, 'response')
    email_body = frappe.render_template(email_body, {"due_diligence_secure_url": f"""{doctype}: {frappe.utils.get_url()+f"/proposal?quotation={urllib.parse.quote(docname)}&doctype={urllib.parse.quote(doctype)}"} """})
    
    if(not Doc.sales_partner):
        frappe.throw("Couldn't find Sales Partner")
    mobile=frappe.get_value("Sales Partner", Doc.sales_partner, "mobile_no")


    if not mobile:
        frappe.throw('Kindly enter Mobile no for Sales Partner')
    
    whatsapp(number = mobile,
    message=[email_body],
    media_type="None")

    url = frappe.utils.get_url()
    return [url, newDocName]

def create_due_diligence(send_to, email_template, contact_person, quotation, source_doctype):
    
    url = frappe.utils.get_url()
    url = url+f"/proposal?quotation={quotation}&doctype={source_doctype}"
    
    url_expiry_days = frappe.db.get_single_value("Due Diligence Settings", "url_expiry_days")
    url_expiry_days = int(url_expiry_days)
    
    after_15_days = add_to_date(datetime.now(), days=url_expiry_days, as_string=True)
    
    
    docs = frappe.new_doc("Due Diligence")
    docs.send_to = send_to
    docs.sender = frappe.session.user
    docs.quotation = quotation
    docs.document_type = source_doctype
    docs.document_name = quotation
    docs.diligence_status = "Sent"
    docs.url = url 
    docs.url_expiry_date = after_15_days
    docs.date_created = datetime.now()
    docs.save()
    
    due_diligence_list = set([])
    due_diligence_list = frappe.get_list('Due Diligence', 
    filters = {
    'diligence_status': ['in','Sent,Viewed,Draft'],
    'name': ['!=', docs.name],
    'document_type': ['=', source_doctype],
    'document_name': quotation,
    }, 
    fields = ["name", "diligence_status"])
    
    if due_diligence_list:
                
        for diligence_name in due_diligence_list:
            if diligence_name:
                docUpdate = frappe.get_doc("Due Diligence", diligence_name)
                docUpdate.diligence_status = "Declined"
                docUpdate.save()
    return docs.name
            

@frappe.whitelist()
def check_due_diligence_settings():
    accepted_template = frappe.db.get_single_value("Due Diligence Settings", "accepted_email_template")
    decline_template = frappe.db.get_single_value("Due Diligence Settings", "decline_email_template")
    
    if (accepted_template == '' or decline_template == ''):
        return {"status": False, "errorMsg": "Kindly select the default Email Template in Due Diligence settings."}
    else:
        return {"status": True}
    
    

@frappe.whitelist()
def get_file_id(name):
    file_id = frappe.db.get_list("File", filters={"attached_to_name": name}, as_list=1)
    return file_id

@frappe.whitelist()
def check_file_private_or_not(quotation_name, source_doctype="Quotation"): 
    file_name = quotation_name+".pdf"
    get_file_id = frappe.db.get_value("File",{"attached_to_doctype": source_doctype, "attached_to_name": quotation_name}, ["name"]) 
    file = frappe.get_doc("File", get_file_id)
    return file.is_private

def due_diligence_schedule():
    doc=frappe.get_all("Due Diligence",pluck="document_name")
    so=frappe.get_all("Sales Order",filters={
        "name": ["not in", doc ],
        "creation": ["<", frappe.utils.nowdate()]
        },fields=["name", "sales_partner"])
    for i in so:
        send_whatsapp_due_diligence(i["sales_partner"], "Due Email", "Sales Order", i["name"])

