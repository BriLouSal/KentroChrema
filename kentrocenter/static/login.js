console.log("LOGIN JS RUNNING");
console.log("Messages:", window.djangoMessages);

if (window.djangoMessages && window.djangoMessages.length > 0) {

    window.djangoMessages.forEach(msg => {

        Swal.fire({
            icon: msg.type || "error",
            title: msg.text,
            toast: true,
            position: "top-end",
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
        });

    });

}