const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");
const header = document.querySelector(".header")

sign_up_btn.addEventListener("click", () => {
  container.classList.add("sign-up-mode");
  header.querySelector(".logo").style.color = "#1976D2"
  header.querySelectorAll(".btn").forEach(btn => {
    btn.style.backgroundColor = '#fff'
    btn.style.color = '#1976D2'
  })

});

sign_in_btn.addEventListener("click", () => {
  container.classList.remove("sign-up-mode");
  header.querySelector(".logo").style.color = "#ffff"
  header.querySelectorAll(".btn").forEach(btn => {
    btn.style.backgroundColor =  '#1976D2'
    btn.style.color = '#fff' 
  })

});
