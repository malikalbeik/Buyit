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


var input = document.getElementById("searchInput");
var awesomplete = new Awesomplete(input, {
	minChars: 1,
});
var timeout = null;


input.addEventListener("input", function(e) {

    if (timeout) {  
        clearTimeout(timeout);
      }

    timeout = setTimeout(function() {
        if (e.target.value) {
            var xhttp = new XMLHttpRequest();
            xhttp.open("GET", `http://127.0.0.1:5000/search?search=${e.target.value}&json=true`, true);
            xhttp.send();
    
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    awesomplete.list = JSON.parse(xhttp.responseText).map(val => ({value: val, label: val}));
                }
            }
        }
    }, 500);
})
