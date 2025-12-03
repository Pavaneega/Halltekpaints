const BACKEND_ORIGIN = 'http://127.0.0.1:5000'; // change if your Flask host/port differs

document.addEventListener('DOMContentLoaded', () => {
  const loginLink = document.getElementById('navLoginLink');
  const logoutButton = document.getElementById('navLogoutButton');
  const rewardsLink = document.getElementById('navRewardsLink');

  async function refreshSessionState() {
    try {
      const res = await fetch(`${BACKEND_ORIGIN}/api/session`, { credentials: 'include' });
      const data = await res.json();
      const authenticated = !!data.authenticated;

      // toggle login / logout
      if (authenticated) {
        if (loginLink) {
          loginLink.hidden = true;
          loginLink.style.display = 'none';
        }
        if (logoutButton) {
          logoutButton.hidden = false;
          logoutButton.style.display = 'inline-block';
          // Update text if username available
          if (data.username) {
             logoutButton.innerHTML = `Logout (${data.username})`;
          }
        }
      } else {
        if (loginLink) {
          loginLink.hidden = false;
          loginLink.style.display = 'inline-block';
        }
        if (logoutButton) {
          logoutButton.hidden = true;
          logoutButton.style.display = 'none';
        }
      }
    } catch (e) {
      console.error('session check failed', e);
    }
  }

  // Intercept Rewards click: require login once
  if (rewardsLink) {
    rewardsLink.addEventListener('click', async (ev) => {
      ev.preventDefault();
      try {
        const res = await fetch(`${BACKEND_ORIGIN}/api/session`, { credentials: 'include' });
        const data = await res.json();
        if (!data.authenticated) {
          window.location.href = `${BACKEND_ORIGIN}/login?next=/rewards`;
        } else {
          window.location.href = rewardsLink.getAttribute('href') || `${BACKEND_ORIGIN}/rewards`;
        }
      } catch (err) {
        window.location.href = `${BACKEND_ORIGIN}/login?next=/rewards`;
      }
    });
  }

  // Logout behavior
  if (logoutButton) {
    logoutButton.addEventListener('click', async () => {
      try {
        await fetch(`${BACKEND_ORIGIN}/logout`, { method: 'GET', credentials: 'include' });
      } catch (e) {
        console.warn('logout request failed', e);
      } finally {
        await refreshSessionState();
        window.location.href = '/';
      }
    });
  }

  // initial state
  refreshSessionState();
});


