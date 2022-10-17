frappe.ready(async () => {
    initialize_quote_content();
});


async function initialize_quote_content() {
    await get_quote_content();
};

async function get_quote_content() {
    // Using await through this file instead of then.
    const queryString = window.location.search;
    const split_string = queryString.split("=");
    window.quotation = (await frappe.call({
        method: 'due_diligence.www.proposal.index.get_content',
        args: {
            "doctype": "Quotation",
            "name": split_string[1],
        },
        callback: function(response){
            if(response.message.status == false){
                window.location.href = response.message.getURL+'/proposal/expire.html';
            } else {
                if(response.message.status){
                    $(document).find('#viewPDF').attr('src', response.message.getURL + '#toolbar=0');
                } else {
                    window.location.href = response.message.getURL+'/proposal/404';
                }
            }
        }
        // callback: function(response){
        //     // console.log(response);
        //     if(response.message.status){
        //         $(document).find('#viewPDF').attr('src', response.message.getURL + '#toolbar=0');
        //         console.log(response.message.getURL);
        //     } else {
        //         window.location.href = response.message.getURL+'/proposal/404';
        //     }
        // }
    })).message;
    return false;
}

function update_due_diligence_on_acceptance(){
    
    const queryString = window.location.search;
    const split_string = queryString.split("=");
    const quotation_name = split_string[1]

    var getAcceptedName = document.getElementById('accept_or_decline_by').value;
    
    let send_email_on_acceptance = frappe.call({
        method: "due_diligence.www.proposal.index.send_mail_on_acceptance_or_decline",
        args: {
            "doctype": "Quotation",
            "name": quotation_name,
            "accept_or_decline_by": getAcceptedName,
            "action": "accept",
            "reason":''
        },
        callback: function(response){
            if (response.message.status) {
                window.location.href = response.message.redirectURL+'/proposal/success';
            }
        }
    }).message;
    return send_email_on_acceptance
}

function update_due_diligence_on_decline(){
    const queryString = window.location.search;
    const split_string = queryString.split("=");
    const quotation_name = split_string[1]

    // var getDeclinedName = document.getElementById('accept_or_decline_by').value;
    var reason = document.getElementById('reason').value;

    let send_email_on_decline = frappe.call({
        method: "due_diligence.www.proposal.index.send_mail_on_acceptance_or_decline",
        args: {
            "doctype": "Quotation",
            "name": quotation_name,
            "accept_or_decline_by": '',
            "action": "decline",
            "reason": reason
        },
        callback: function(response){
            if (response.message.status) {
                window.location.href = response.message.redirectURL+'/proposal/decline';
            }
        }
    }).message;
    return send_email_on_decline
}

function validateForm() {

    let checkbox = document.getElementById('acceptance');
    let accept_by = document.getElementById('accept_or_decline_by').value;
    if(checkbox.checked == false) {
        alert('Please fill checkbox');
        return false;
    } 
    
    if(accept_by.trim() == ''){
        alert('Please fill name');
        return false;
    }

    update_due_diligence_on_acceptance();
}

function redirect(){
    const queryString = window.location.search;
    const split_string = queryString.split("=");
    const quotation_name = split_string[1]

    let url = frappe.call({
        method: "due_diligence.www.proposal.index.get_url",
        args:{
            "doctype": "Quotation",
            "name": quotation_name,
            "accept_or_decline_by": '',
        },
        callback: function(response){
            window.location.href = response.message[0]+'/proposal/reason'+'?quotation='+response.message[2];
        }
    }).message;
    return url;
}
