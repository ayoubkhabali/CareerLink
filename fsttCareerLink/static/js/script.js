const navbar = document.querySelector(".header")
// const loginBtn = document.querySelector(".loginBtn")
// const loginForm = document.querySelector(".login-modal")

// loginBtn.addEventListener("click", (e) => {
//     e.preventDefault()
//     console.log("class addedd!!")
//     loginForm.classList.add("showModal")
    
// })

window.addEventListener('scroll', ()=> {
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});
