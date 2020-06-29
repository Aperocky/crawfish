import * as button from "./buttons.js";
import * as util from "./util.js";


function write_author_data() {
    let base = document.getElementById("first");
    util.clearElement(base);
    let desc = util.addElement(base, "div", "col-md-6");
    let imgs = util.addElement(base, "div", "col-md-6");
    if (this.response["image_samples"].length > 1) {
        let sample = util.addElement(imgs, "img");
        let src = this.response["image_samples"][0].split("highway/")[1];
        sample.setAttribute("src", "/static/symlink/" + src);
        sample.style.maxHeight = "750px";
    }
    let title = util.addElement(desc, "h3");
    title.textContent = this.response["auth_name"];
    let auth_id = util.addElement(desc, "p", "lead");
    auth_id.textContent = this.response["auth_id"];
    write_author_info_block(desc, this.response["auth_info"]);
}


function write_author_info_block(desc, dict) {
    let table = util.addElement(desc, "table", "table");
    let thead = util.addElement(table, "thead");
    let tbody = util.addElement(table, "tbody");
    let descs = util.addElement(thead, "th");
    descs.textContent = "Attribute";
    let vals = util.addElement(thead, "th");
    vals.textContent = "Value";
    for (const [key, val] of Object.entries(dict)) {
        let tlevel = util.addElement(tbody, "tr");
        let tdesc = util.addElement(tlevel, "td");
        let tval = util.addElement(tlevel, "td");
        tdesc.textContent = key;
        tval.textContent = val;
    }
}


button.randomButton.addEventListener("click", () => {
    util.ajaxGet("/auth/random", write_author_data);
});


button.sampleButton.addEventListener("click", () => {
    util.ajaxGet("/auth/sample_img", write_author_data);
});
