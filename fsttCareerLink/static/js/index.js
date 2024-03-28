const sideLinks = document.querySelectorAll('.sidebar .side-menu li a:not(.logout)');

sideLinks.forEach(item => {
    const li = item.parentElement;
    item.addEventListener('click', () => {
        sideLinks.forEach(i => {
            i.parentElement.classList.remove('active');
        })
        li.classList.add('active');
    })
});

const menuBar = document.querySelector('.content nav .bx.bx-menu');
const sideBar = document.querySelector('.sidebar');

menuBar.addEventListener('click', () => {
    sideBar.classList.toggle('close');
});

const searchBtn = document.querySelector('.content nav form .form-input button');
const searchBtnIcon = document.querySelector('.content nav form .form-input button .bx');
const searchForm = document.querySelector('.content nav form');

searchBtn.addEventListener('click', function (e) {
    if (window.innerWidth < 576) {
        e.preventDefault;
        searchForm.classList.toggle('show');
        if (searchForm.classList.contains('show')) {
            searchBtnIcon.classList.replace('bx-search', 'bx-x');
        } else {
            searchBtnIcon.classList.replace('bx-x', 'bx-search');
        }
    }
});

window.addEventListener('resize', () => {
    if (window.innerWidth < 768) {
        sideBar.classList.add('close');
    } else {
        sideBar.classList.remove('close');
    }
    if (window.innerWidth > 576) {
        searchBtnIcon.classList.replace('bx-x', 'bx-search');
        searchForm.classList.remove('show');
    }
});



const actionBtns = document.querySelectorAll(".post-actions .btn");
actionBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        btn.classList.toggle("btn-active")
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('.filtering-posts .profile-tab');
    const posts = document.querySelectorAll('.your-posts .post');

    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const filter = this.dataset.filter;

            tabs.forEach(t => t.classList.remove('current-tab'));
            this.classList.add('current-tab');

            posts.forEach(post => {
                if (filter === 'all' || post.dataset.type === filter) {
                    post.style.display = 'block';
                } else {
                    post.style.display = 'none';
                }
            });
        });
    });
});

const modalBtn = document.querySelectorAll(".modal-trigger")
const modalBox = document.querySelector(".overlay")


modalBtn.forEach(btn => {
    btn.addEventListener("click", ()=> {
        modalBox.classList.toggle("show-modal")
        if (btn.dataset.formType === 'announcement')
            modalBox.querySelector(".overlay .announcement-modal").style.display = 'block'
        if (btn.dataset.formType === 'assignment')
            modalBox.querySelector(".overlay .assignment-modal").style.display = 'block'
        if (btn.dataset.formType === 'class')
            modalBox.querySelector(".overlay .class-modal").style.display = 'block'
         

    })
})

modalBox.addEventListener("click", (event) => {
  if (event.target === modalBox) {
    modalBox.classList.remove("show-modal"); // Remove the class
    modalBox.querySelectorAll(".overlay .modal").forEach(modal => {modal.style.display ='none'})  }
});

















const messages = document.querySelector('.messages');
const message = messages.querySelectorAll('.message');
const messageSearch = document.querySelector('#message-search');

const searchMessage = () => {
    const val = messageSearch.value.toLowerCase();
    message.forEach(user => {
        let name = user.querySelector('h5').textContent.toLowerCase();
        if(name.indexOf(val) != -1) {
            user.style.display = 'flex'; 
        } else {
            user.style.display = 'none';
        }
    })
}

messageSearch.addEventListener('keyup', searchMessage);