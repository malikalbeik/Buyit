/**
 * ===========
 * app.js
 * ===========
 * 
 * app.js containes the javascript that will run in the app.
 * 
*/


// Initiating varaibles that will be used in the loadMoreItems()
var offset = 8;
const incrementNum = 8;

// Initiating Awesomplete in #seachInput with a minimum characters of 1.
var awesomplete = new Awesomplete(document.getElementById("searchInput"), {
	minChars: 1,
});


/**
 * when called fetchs more items from the server and adds them to the ul in index.html,
 * if there is no elements returned by the server it hides the loadMore button and shows
 * the paragram telling the user that there is no items left.
 */
function loadMoreItems() {
    var ul = document.querySelector(".elements");
    var category = (ul.classList[0] == "items" ? "" : ul.classList[0])
    fetch(`http://127.0.0.1:5000/getelements?offset=${offset}&limit=${incrementNum}&category=${category}`)
    .then((resp) => resp.json())
    .then((res) => {
        console.log(res);
        if (res.length != 0) {
            offset += incrementNum;
            var li;
            res.map(function(element) {
                li = document.createElement("li");
                li.innerHTML = `<a href="items/${element.id}"><img src="/static/photos/${element.photos_dir}" alt="TO-DO"><h3>${element.name}</h3></a>`
                ul.appendChild(li);
            })
        }
        else {
            document.querySelector(".load-more > p").style.display = "block";
            document.querySelector(".load-more > button").style.display = "none";
        }
    })
}


/**
 * When called opens the sideMenu and adds an even listener to the body
 * the event listener checks for clicks that are made outside the sideMenu
 * and then calls the colseNav() function.
 */
function openNav() {
    document.querySelector(".sideMenu").style.width = "250px";
    document.getElementById("overlay").style.display = "block";
    document.querySelector("body").style.overflow = "hidden";
    
    
    document.querySelector("body").addEventListener("click", (event) => {
        if (event.target != document.querySelector(".sideMenu") && event.target != document.querySelector(".avatar img")) {
            closeNav();
        }
    })
}


/**
 * When called closes the sideMenu.
 */
function closeNav() {
    document.querySelector(".sideMenu").style.width = "0";
    document.getElementById("overlay").style.display = "none";
    document.querySelector("body").style.overflow = "auto";
}


/**
 * Makes a fetch request to the server requesting the autocompletion words 
 * that match `value` then maps over the words putting eachone to awesomplete's
 * list.
 * 
 * @param {String} value - A string containing the value the user has entered
 */
var awesompleteComplete = debounce(function(value) {
    if (value) {
        fetch(`http://127.0.0.1:5000/search?search=${value}&json=true`)
        .then((resp) => resp.json())
        .then((data) => {
            awesomplete.list = data.map(val => ({value: val.name, label: val.name}));
        })
    }
}, 500)


/**
 * Credit: David Walsh (https://davidwalsh.name/javascript-debounce-function)
 * 
 * [Returns a function, that, as long as it continues to be invoked, will not
 * be triggered. The function will be called after it stops being called for
 * N milliseconds. If `immediate` is passed, trigger the function on the
 * leading edge, instead of the trailing.]
 * 
 * @param {function} func - The function to be excuted.
 * @param {number} wait - The time in milliseconds.
 * @param {Boolean} immediate - A Boolean to know if the functino should be exuted immediately.
 */
function debounce(func, wait, immediate) {
    var timeout;
  
    return function executedFunction() {
      var context = this;
      var args = arguments;
          
      var later = function() {
        timeout = null;
        if (!immediate) func.apply(context, args);
      };
  
      var callNow = immediate && !timeout;
      
      clearTimeout(timeout);
  
      timeout = setTimeout(later, wait);
      
      if (callNow) func.apply(context, args);
    };
  };
