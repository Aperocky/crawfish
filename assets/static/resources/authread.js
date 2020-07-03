import * as util from "./util.js";


function writeAuthorData() {
    let base = document.getElementById("first");
    util.clearElement(base);
    let desc_col = util.addElement(base, "div", "col-md-6");
    let desc = util.addElement(desc_col, "div", "row");
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
    let infodict = this.response["auth_info"];
    infodict["score"] = this.response["auth_score"]
    writeAuthorInfoBlock(desc, infodict);
    writeAuthmodBlock(desc_col, this.response["auth_id"], this.response["image_atlarge"]);
}


function writeUncrawledSamples(desc_col, list) {
    let desc = util.addElement(desc_col, "div", "row");
    let ul = util.addElement(desc, "ul");
    let count = 0;
    for (let src of list) {
        count += 1;
        let li = util.addElement(ul, "li");
        let a = util.addElement(li, "a");
        a.setAttribute("href", src);
        a.setAttribute("rel", 'noreferrer');
        a.textContent = `sample ${count}`;
    }
}


function writeAuthorInfoBlock(desc, dict) {
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


function writeAuthmodBlock(desc_col, author_id, image_atlarge) {
    let authmod = util.addElement(desc_col, "div", "row");
    let reconButton = util.addElement(authmod, "button", "btn btn-info");
    let refreshButton = util.addElement(authmod, "button", "btn btn-info");
    let inspectButton = util.addElement(authmod, "button", "btn btn-info");
    reconButton.textContent = "RECON";
    refreshButton.textContent = "REFRESH";
    inspectButton.textContent = "INSPECT";
    for (let each of [reconButton, refreshButton, inspectButton]) {
        each.style.display = "inline-block";
        each.style.margin = "10px";
    }
    reconButton.addEventListener("click", () => {
        util.ajaxGet(`/write/recon_id?author_id=${author_id}`, util.alertResults);
    });
    refreshButton.addEventListener("click", () => {
        util.ajaxGet(`/read/refresh`, writeAuthorData);
    });
    inspectButton.addEventListener("click", () => {
        let count = 0;
        for (let image of image_atlarge) {
            count ++;
            window.open(image, `im_${count}`, 'noreferrer', 'noopener');
        }
    });
}


let randomButton = document.getElementById("random");
let sampleButton = document.getElementById("sample");


randomButton.addEventListener("click", () => {
    util.ajaxGet("/read/random", writeAuthorData);
});


sampleButton.addEventListener("click", () => {
    util.ajaxGet("/read/sample_img", writeAuthorData);
});
