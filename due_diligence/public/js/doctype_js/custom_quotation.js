frappe.ui.form.on('Quotation', {
    refresh: function(frm){
        if (frm.doc.docstatus == 1){
            cur_frm.add_custom_button(__('Send Due Diligence'), function(){
                cur_frm.trigger("customValidation");
            });
        }
    },
    

    customValidation: function(frm){
        if(cur_frm.doc.contact_email == '' || cur_frm.doc.contact_email == undefined){
            frappe.throw(__('Kindly select the contact.'));
            return false;
        }
        else {
            /* check Due Diligence Settings for email template */
            frappe.call({
                method: "due_diligence.due_diligence.doctype.due_diligence.due_diligence.check_due_diligence_settings",
                callback: function(response){
                    if (response.message.status) {
                        cur_frm.trigger("due_diligence");
                    } else {
                        if (response.message.errorMsg != '') {
                            frappe.msgprint(response.message.errorMsg);
                        } else {
                            frappe.msgprint("Something went wrong!");
                        }
                    }
                }
            });
        }
    },

    due_diligence: function(frm){
        let dialog = new frappe.ui.Dialog({
            title: __("Send Due Diligence"),
            fields: [
                {
                    label: __('Person'),
                    fieldtype: 'Data',
                    fieldname: 'contact_person',
                    reqd:1,
                    // options: frm.doc.contact_display,
                },
                
                {
                    label: __('Email Template'),
                    fieldtype: 'Link',
                    fieldname: 'email_template',
                    options: 'Email Template',
                    req: 1,
                    onchange: function(e) {
                        if(this.value != ''){
                            frappe.call({
                                method:"due_diligence.due_diligence.doctype.due_diligence.due_diligence.get_email_template_details",
                                args:{
                                    "doctype":"Email Template",
                                    "name": this.value,
                                    "quotationName": frm.doc.name
                                },
                                callback: function(response){
                                    dialog.set_value("email_subject", response.message[0]);
                                    dialog.set_value("email_body", response.message[1]);
                                }
                            });
                        }
                    }
                },
                {
					fieldtype: 'Column Break',
					fieldname: 'col_break_1',
				},
                {
                    label: __('Send To'),
                    fieldtype: 'Data',
                    fieldname: 'send_to',
                    reqd:1,
                    // options: frm.doc.contact_email
                }, 
                {
					fieldtype: 'Section Break',
					fieldname: 'sec_break_1',
				},
                {
                    label: __('Email Subject'),
                    fieldtype: 'Data',
                    fieldname: 'email_subject',
                    req:1,
                },
               
                {
                    label: __("Email Body"),
                    fieldtype: 'Text Editor',
                    fieldname: 'email_body',
                    req:1
                },
                {
					fieldtype: 'Section Break',
					fieldname: 'sec_break_1',
				},
                // {
				// 	fieldtype: 'Column Break',
				// 	fieldname: 'col_break_5',
				// },
                {
                    label: __('Send Email'),
                    fieldtype: 'Button',
                    fieldname: 'send_email',
                    click: function(){

                        if(dialog.get_value("contact_person") == '' || dialog.get_value("contact_person") == null) {
                            frappe.throw("Please Select Person !");
                            return false;
                        }
                        if(dialog.get_value("send_to") == '' || dialog.get_value('send_to') == null) {
                            frappe.throw("Please Select Send To !");
                            return false;
                        }
                        
                        frappe.call({
                            method:"due_diligence.due_diligence.doctype.due_diligence.due_diligence.send_email_due_diligence",
                            args: {
                                "send_to": dialog.get_value("send_to"),
                                "email_template": dialog.get_value("email_template"),
                                "contact_person": dialog.get_value("contact_person"),
                                "quotation": frm.doc.name,
                            },
                            callback:function(response){
                                // console.log(frappe.local.request_ip);
                                console.log(response.message);
                                if (response.message) {
                                    location.href = response.message[0] + "/app/due-diligence/" + response.message[1];
                                    } 
                            }
                        });
                        dialog.hide();
                    }
                },
                {
					fieldtype: 'Column Break',
					fieldname: 'col_break_5',
				},
                {
                    label: __("Cancel"),
                    fieldtype: "Button",
                    fieldname: "cancel",
                    click: function(){
                        dialog.hide();
                    }
                }
            ]
        });
        dialog.set_value("contact_person",frm.doc.contact_display);
        dialog.set_value("send_to",frm.doc.contact_email);
        dialog.show();
        dialog.$wrapper.find('.modal-dialog').css({"max-width": "1000px"});
        dialog.$wrapper.find('.modal-content').css({"width": "1000px"});
        dialog.$wrapper.find('.ql-editor').css({"min-height": "150px"});
        dialog.$wrapper.find('button[data-fieldname=send_email]').css({'background-color': '#2490ef','float':'left', 'color': '#ffffff'});
        dialog.$wrapper.find('button[data-fieldname=cancel]').css({'background-color': 'red','float':'right','color': '#ffffff'});
    },
});



frappe.ui.form.on("Quotation", {
    onload: function(frm) {
        var fileName = frm.doc.name+'.pdf';
        $('a[title="'+fileName+'"]').removeAttr('href', 'javascript://');
        $('a[title="'+fileName+'"]').on('click', function(){
            var getFileUrl = window.location.href;
            var http_https = getFileUrl.split(/[/?#]/)[0];
            var domain = http_https+'//'+getFileUrl.replace('http://','').replace('https://','').split(/[/?#]/)[0];

            frappe.call({
                method: "due_diligence.due_diligence.doctype.due_diligence.due_diligence.check_file_private_or_not",
                args: {
                    "quotation_name": frm.doc.name,
                },
                callback: function(response){

                    var getFileUrl = domain+'/files/'+fileName;
                    if (response.message) {
                        getFileUrl = domain+'/private/files/'+fileName;
                    }

                    let dialog = new frappe.ui.Dialog({
                        title: __('Preview File'),
                        fields: [
                            {
                                label: __('Note'),
                                fieldtype: 'HTML',
                                fieldname: 'note'
                            }
                        ]
                    });
            
                    dialog.fields_dict.note.$wrapper.append('<iframe src="' + getFileUrl + '#toolbar=0&navpanes=0" style="zoom:0.60;z-index:1099 !important;" frameborder="0" width="99.5%" height="630px" scrolling="no"></iframe>');
                    dialog.$wrapper.find('.modal-dialog').css({"max-width": "1000px"});
                    dialog.$wrapper.find('.modal-content').css({"height": "500px", "width": "1000px"});
                    dialog.show();
                }
            })

            return false;
            
        });
    }
});