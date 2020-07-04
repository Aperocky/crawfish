// Ajax handler
export function ajaxGet(url, handler) {
    let req = new XMLHttpRequest();
    req.addEventListener('load', handler);
    req.open("get", url);
    req.responseType = 'json';
    req.send();
}

export function ajaxPost(url, content, handler) {
    let req = new XMLHttpRequest();
    req.addEventListener('load', handler);
    req.open("post", url);
    req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    req.responseType = 'json';
    req.send(JSON.stringify(content));
}

export function addElement(parent, etype, className="") {
    let e = document.createElement(etype);
    parent.appendChild(e);
    e.className = className;
    return e;
}

export function clearElement(element) {
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
}


export function alertResults() {
    alert(JSON.stringify(this.response));
}

