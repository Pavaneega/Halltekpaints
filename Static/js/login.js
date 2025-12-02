document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('.auth-form');
  if (!form) return;

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton ? submitButton.textContent : '';

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = 'Logging in...';
    }

    const formData = new FormData(form);
    const body = new URLSearchParams(formData);

    // Decide which backend URL to hit.
    // If you're viewing the site via a static server on port 5500,
    // send the request to the Flask backend on port 5000.
    const isStaticServer = window.location.port === '5500';
    const baseUrl = isStaticServer ? 'http://127.0.0.1:5000' : '';

    try {
      const response = await fetch(`${baseUrl}/login`, {
        method: 'POST',
        headers: {
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        },
        credentials: 'include',
        body
      });

      if (!response.ok) {
        // Try to read error page text for debugging
        const text = await response.text();
        console.error('Login failed with status', response.status, text);
        alert('Login failed. Please check your username and password.');
        return;
      }

      // On success, redirect back to port 5500
      window.location.href = 'http://127.0.0.1:5500/templates/index.html';
    } catch (error) {
      console.error('Login request failed:', error);
      alert('Login failed. Please check your connection and try again.');
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = originalText;
      }
    }
  });
});


