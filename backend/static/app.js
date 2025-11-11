// Mobile nav toggle
document.addEventListener('DOMContentLoaded', ()=>{
  const navToggle = document.getElementById('navToggle');
  const nav = document.getElementById('nav');
  if(navToggle){
    navToggle.addEventListener('click', ()=>{
      nav.classList.toggle('show');
    });
  }

  // Sidebar toggle for mobile
  const sidebarToggle = document.getElementById('sidebarToggle');
  if(sidebarToggle){
    sidebarToggle.addEventListener('click', ()=>{
      const sidebarNav = document.querySelector('.sidebar-nav');
      if(sidebarNav) sidebarNav.classList.toggle('show');
    });
  }

  // Smooth scrolling for internal links
  document.querySelectorAll('a[href^="#"]').forEach(a=>{
    a.addEventListener('click', (e)=>{
      const href = a.getAttribute('href');
      if(!href || href === '#') return;
      e.preventDefault();
      const el = document.querySelector(href);
      if(el) el.scrollIntoView({behavior:'smooth',block:'start'});
    });
  });

  // Optional: subscribe form (if you add one)
  const subscribe = document.querySelector('#subscribeForm');
  if(subscribe){
    subscribe.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const email = subscribe.querySelector('input[type=email]').value;
      if(!email) return alert('Enter your email');
      // Fake success for demo
      alert('Thanks! We will notify you — ' + email);
      subscribe.reset();
    });
  }

  // Close modals when clicking outside
  const modals = document.querySelectorAll('.modal');
  modals.forEach(modal => {
    modal.addEventListener('click', (e) => {
      if(e.target === modal) modal.style.display = 'none';
    });
  });
});
