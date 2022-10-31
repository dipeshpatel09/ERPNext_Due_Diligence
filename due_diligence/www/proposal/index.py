
import frappe
import json
from frappe.desk.form.load import get_attachments
from frappe.utils.pdf import get_pdf
from datetime import datetime 
from frappe.utils import get_url
from frappe import _
from frappe.core.doctype.communication.email import make
from frappe.utils.file_manager import get_file_path
from frappe.utils import encode
from frappe.utils import today, getdate
from datetime import datetime

no_cache = 1

@frappe.whitelist(allow_guest = True)
def get_content(doctype, name, format=None):
    due_diligence = frappe.db.get_list("Due Diligence", filters={'quotation': name, 'diligence_status':'Sent'}, fields=['name'])
    diligence = frappe.db.get_all("Due Diligence", filters={'quotation': name, 'diligence_status':'Sent'}, as_list=1)
    diligence = diligence[2:23]
    diligence_name = frappe.get_doc("Due Diligence", diligence)
    url_expiry_date = diligence_name.url_expiry_date
    current_date = getdate()
    diligence_status = diligence_name.diligence_status
    if(current_date >= url_expiry_date):
        return {'status': False, 'Msg': 'URL is Expired !', 'getURL': frappe.utils.get_url(), 'diligence_status':diligence_status}
    else:
        if due_diligence:
            file_name = name+".pdf"
            get_file_id = frappe.db.get_value("File",{"file_name": file_name}, ["name"])
            file = frappe.get_doc("File", get_file_id)
            
            getFileURL = frappe.utils.get_url() + file.file_url
            return {'status': True, 'getURL': getFileURL}
        else:
            return {'status': False, 'getURL': frappe.utils.get_url(), 'diligence_status': diligence_status}

   
@frappe.whitelist(allow_guest = True)
def send_mail_on_acceptance_or_decline(doctype, name, accept_or_decline_by, action, reason):
    
    file_name = name+".pdf"
    get_file_id = frappe.db.get_value("File",{"file_name": file_name}, ["name"])
    file = frappe.get_doc("File", get_file_id)
    file_path = get_file_path(file.file_url)
    with open(encode(file_path), "rb") as fileobj:
        filedata = fileobj.read()
    out = {
    		"fname": file.file_name,
    		"fcontent": filedata 
    	}
    redirect_url = frappe.utils.get_url()
    
    quotationDoc = frappe.get_doc("Quotation", name)
    docAsDict = quotationDoc.as_dict()
    

    if (action == 'accept'):
        customer_email = frappe.db.get_value(doctype, name, 'contact_email')
        email_template = frappe.db.get_single_value("Due Diligence Settings", "accepted_email_template")
        email_subject, email_body = frappe.db.get_value("Email Template", email_template, ["subject", "response"])
        email_body = frappe.render_template(email_body, docAsDict)
        recipients =  customer_email
        email_cc = frappe.db.get_single_value("Due Diligence Settings", "email_cc")
        # doc = frappe.get_doc("Quotation", name)
        attachments = [out]
        # attachment = attachments.append(frappe.attach_print(doctype, name, doc=doc))
    elif(action == 'decline'):
        email_template = frappe.db.get_single_value("Due Diligence Settings", "decline_email_template")
        email_subject, email_body = frappe.db.get_value("Email Template", email_template, ["subject", "response"])
        email_body = frappe.render_template(email_body, docAsDict)
        recipients =  frappe.db.get_value("Due Diligence", {'quotation': name},["sender_email"])
        attachments = ''
        email_cc = ''
        
    result = update_due_diligence(doctype, name, accept_or_decline_by, action, reason)
    
    
    frappe.sendmail(
        recipients =  recipients,
        subject = email_subject,
        message = email_body,
        attachments = attachments,
        cc = email_cc,
        delayed = False,
    )
    
    if frappe.session.user == "Guest":
        frappe.msgprint("Email Sent")
    return {'status': result, 'redirectURL': redirect_url}
    
@frappe.whitelist(allow_guest = True)   
def update_due_diligence(doctype, name, accept_or_decline_by, action, reason):
    due_diligence = frappe.db.get_value("Due Diligence",{"diligence_status": "Sent"}, ["name"])
    due_diligence_doc = frappe.get_doc("Due Diligence",due_diligence)
    
    if due_diligence_doc.name:
        if(action == 'accept'):
            due_diligence_doc.accepted_date = datetime.now()
            due_diligence_doc.accepted_name = accept_or_decline_by
            due_diligence_doc.diligence_status = "Accepted Digitally"
        elif(action == 'decline'):
            due_diligence_doc.decline_date = datetime.now()
            due_diligence_doc.diligence_status = "Declined"
            due_diligence_doc.decline_reason = reason
        due_diligence_doc.save()
    return True
    
   
@frappe.whitelist(allow_guest = True)
def get_url(doctype, name, accept_or_decline_by):
    url = frappe.utils.get_url()
    return [url, doctype, name, accept_or_decline_by] 



