function openNav() {
    document.querySelector(".sideMenu").style.width = "250px";
    document.getElementById("overlay").style.display = "block";
    document.querySelector("body").style.overflow = "hidden";
    
    
    document.querySelector("#main").addEventListener("click", (event) => {
        if (event.target != document.querySelector(".sideMenu") && event.target != document.querySelector(".avatar img")) {
            closeNav();
        }
    })
}

function closeNav() {
    document.querySelector(".sideMenu").style.width = "0";
    document.getElementById("overlay").style.display = "none";
    document.querySelector("body").style.overflow = "auto";
}
