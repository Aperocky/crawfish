import * as util from "./util.js";

var CURRENT_AUTHOR_ID = '000000';

function writeAuthorData() {
    let base = document.getElementById("first");
    util.clearElement(base);
    let desc_col = util.addElement(base, "div", "col-md-6");
    let desc = util.addElement(desc_col, "div", "row");
    let imgs = util.addElement(base, "div", "col-md-6");
    imgs.setAttribute("id", "img_col");
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
    CURRENT_AUTHOR_ID = this.response["auth_id"];
    let infodict = this.response["auth_info"];
    infodict["score"] = this.response["auth_score"]
    writeAuthorInfoBlock(desc, infodict);
    writeJudgements(desc_col, this.response);
    writeAuthmodBlock(desc_col, this.response["auth_id"], this.response["image_atlarge"]);
}


function updateSample() {
    let img_col = document.getElementById("img_col");
    util.clearElement(img_col);
    if (this.response["img"].length > 0) {
        let sample = util.addElement(img_col, "img");
        let src = this.response["img"][0].split("highway/")[1];
        sample.setAttribute("src", "/static/symlink/" + src);
        sample.style.maxHeight = "750px";
    }

//    if (this.response["image_samples"].length > 1) {
//        let sample = util.addElement(img_col, "img");
//        let src = this.response["image_samples"][0].split("highway/")[1];
//        sample.setAttribute("src", "/static/symlink/" + src);
//        sample.style.maxHeight = "750px";
//    }
}


function writeJudgements(desc_col, response) {
    // Judgement line elements
    let desc = util.addElement(desc_col, "div", "row");
    let ldesc = util.addElement(desc, "div", "col-md-1");
    let lval = util.addElement(desc, "div", "col-md-2");
    let xdesc = util.addElement(desc, "div", "col-md-1");
    let xval = util.addElement(desc, "div", "col-md-2");
    let finis = util.addElement(desc, "div", "col-md-2");
    let status = util.addElement(desc, "div", "col-md-4");
    let finisBut = util.addElement(finis, "button", "btn btn-primary");
    let statusBut = util.addElement(status, "button", "btn btn-warning");
    let linput = util.addElement(lval, "input", "form-control");
    let xinput = util.addElement(xval, "input", "form-control");
    // Judgement line content
    ldesc.textContent = "颜";
    xdesc.textContent = "色";
    finisBut.textContent = "审";
    statusBut.textContent = "0";
    linput.setAttribute("id", "linput");
    xinput.setAttribute("id", "xinput");
    statusBut.setAttribute("id", "statusBut");
    linput.setAttribute("placeholder", "N/A");
    xinput.setAttribute("placeholder", "N/A");

    // Add post event
    finisBut.addEventListener("click", () => {
        let lvalue = parseInt(linput.value);
        let xvalue = parseInt(xinput.value);
        if (isNaN(lvalue) || isNaN(xvalue)) {
            console.log(lvalue, xvalue);
            alert("Values are not integer");
            return;
        }
        let post = {
            "l_judge": lvalue,
            "x_judge": xvalue,
            "author": response["auth_name"],
            "author_id": response["auth_id"],
            "thread_count": response["auth_info"]["thread_count"],
            "image_count": response["auth_info"]["image_count"],
            "update_count": response["auth_info"]["update_count"],
            "avg_replies": response["auth_info"]["avg_replies"]
        };
        util.ajaxPost("/write/judge_id", post, postJudgement);
        setTimeout(() => {
            util.ajaxGet(`/read/judgement?author_id=${response["auth_id"]}`, getJudgement);
        }, 500);
    })
    util.ajaxGet(`/read/judgement?author_id=${response["auth_id"]}`, getJudgement);
}


function postJudgement() {
    if (this.response["success"]) {
        alert("JUDGEMENT ACCEPTED");
    } else {
        alert(`Judgement failed: ${this.response["reason"]}`);
    }
}


function getJudgement() {
    console.log(this.response);
    if (this.response["success"]) {
        document.getElementById("linput").setAttribute("placeholder", this.response["l_judge"]);
        document.getElementById("xinput").setAttribute("placeholder", this.response["x_judge"]);
        document.getElementById("statusBut").setAttribute("class", "btn btn-success");
        document.getElementById("statusBut").textContent = (this.response["times_judged"] + 1).toString();
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


function processSelect() {
    if (this.response['success']) {
        console.log(this.response);
        let author_id = this.response["author_id"]
        util.ajaxGet(`/read/find?author_id=${author_id}`, writeAuthorData);
    } else {
        console.log(this.response);
    }
}


let randomButton = document.getElementById("random");
let sampleButton = document.getElementById("sample");
let searchButton = document.getElementById("search");
let luckButton = document.getElementById("select_random");


if (randomButton != null) {
    randomButton.addEventListener("click", () => {
        // util.ajaxGet("/read/random", writeAuthorData);
        util.ajaxGet("/read/random?crawled=true", writeAuthorData);
        // util.ajaxGet("/read/random?tojudge=true&above_l=3&above_x=4", writeAuthorData);
    });
}


if (sampleButton != null) {
    sampleButton.addEventListener("click", () => {
        // util.ajaxGet("/read/sample_img", updateSample);
        let content = {
            'author_id': CURRENT_AUTHOR_ID,
        }
        util.ajaxPost("/getimg/", content, updateSample);
    });
}


if (searchButton != null) {
    searchButton.addEventListener("click", () => {
        let author_id = document.getElementById("search_input").value;
        util.ajaxGet(`/read/find?author_id=${author_id}`, writeAuthorData);
    });
}


if (luckButton != null) {
    luckButton.addEventListener("click", () => {
        let l_arg = document.getElementById("l_arg").value;
        let x_arg = document.getElementById("x_arg").value;
        let content = {
            'l_arg': l_arg,
            'x_arg': x_arg,
        }
        console.log(content);
        util.ajaxPost('/search/', content, processSelect);
    });
}
