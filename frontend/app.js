// Mobile nav toggle
document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.getElementById('navToggle');
  const nav = document.getElementById('nav');
  if(navToggle) {
    navToggle.addEventListener('click', () => {
      nav.classList.toggle('show');
    });
  }

  // Sidebar toggle for mobile
  const sidebarToggle = document.getElementById('sidebarToggle');
  if(sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
      const sidebarNav = document.querySelector('.sidebar-nav');
      if(sidebarNav) sidebarNav.classList.toggle('show');
    });
  }

  // Smooth scrolling for internal links
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const href = a.getAttribute('href');
      if(!href || href === '#') return;
      e.preventDefault();
      const el = document.querySelector(href);
      if(el) el.scrollIntoView({behavior: 'smooth', block: 'start'});
    });
  });

  // Close modals when clicking outside
  const modals = document.querySelectorAll('.modal');
  modals.forEach(modal => {
    modal.addEventListener('click', (e) => {
      if(e.target === modal) {
        modal.style.display = 'none';
      }
    });
  });

  // Form error handling and validation
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      // Basic validation for required fields
      const requiredFields = form.querySelectorAll('[required]');
      let isValid = true;
      
      requiredFields.forEach(field => {
        if(!field.value.trim()) {
          isValid = false;
          field.style.borderColor = '#ef4444';
          field.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
        } else {
          field.style.borderColor = 'rgba(255,255,255,0.06)';
          field.style.boxShadow = 'none';
        }
      });

      if(!isValid) {
        e.preventDefault();
        alert('❌ Please fill in all required fields');
        return false;
      }
    });
  });

  // Modal close handlers
  document.querySelectorAll('.modal-close, #closeModal').forEach(btn => {
    if(btn) {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        const modal = this.closest('.modal');
        if(modal) modal.style.display = 'none';
      });
    }
  });

  // Cancel button handlers
  document.querySelectorAll('#cancelModal').forEach(btn => {
    if(btn) {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        const modal = this.closest('.modal');
        if(modal) modal.style.display = 'none';
      });
    }
  });

  // Password input error clearing
  document.querySelectorAll('input[type="password"], input[type="email"], input[type="text"]').forEach(input => {
    input.addEventListener('input', function() {
      this.style.borderColor = 'rgba(255,255,255,0.06)';
      this.style.boxShadow = 'none';
      // Clear error messages
      const errorElement = this.parentElement.querySelector('.error');
      if(errorElement) {
        errorElement.textContent = '';
      }
    });
  });

  console.log('✅ App initialized successfully');
});