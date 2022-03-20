let btn = document.querySelector(".button");
let qr_code_element = document.querySelector(".qr-code");

btn.addEventListener("click", () => {
    const user_input = `
name: ${document.querySelector("#name_input").value}
address: ${document.querySelector("#address_input").value}
contact_number: ${document.querySelector("#contact_number_input").value}
room_id: ${document.querySelector("#room_id_input").value}
`.trim()

    if (user_input.value != "") {
        if (qr_code_element.childElementCount == 0) {
            generate(user_input);
        } else {
            qr_code_element.innerHTML = "";
            generate(user_input);
        }
    } else {
        console.log("not valid input");
        qr_code_element.style = "display: none";
    }
})

function generate(user_input) {

    qr_code_element.style = "";

    var qrcode = new QRCode(qr_code_element, {
        text: user_input,
        width: 180, //128
        height: 180,
        colorDark: "#000000",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.H
    });

    let download = document.createElement("button");
    qr_code_element.appendChild(download);

    let download_link = document.createElement("a");
    download_link.setAttribute("download", "qr_code.png");
    download_link.innerText = "Download";

    download.appendChild(download_link);

    let qr_code_img = document.querySelector(".qr-code img");
    let qr_code_canvas = document.querySelector("canvas");

    if (qr_code_img.getAttribute("src") == null) {
        setTimeout(() => {
            download_link.setAttribute("href", `${qr_code_canvas.toDataURL()}`);
        }, 300);
    } else {
        setTimeout(() => {
            download_link.setAttribute("href", `${qr_code_img.getAttribute("src")}`);
        }, 300);
    }
}
