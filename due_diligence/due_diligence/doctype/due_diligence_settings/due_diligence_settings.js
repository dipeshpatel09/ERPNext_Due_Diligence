// Copyright (c) 2022, Offshore Evolution Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Due Diligence Settings', {
	onload: function(frm) {
		frm.set_value("url_expiry_days", "15");
		frm.save();
	}
});
