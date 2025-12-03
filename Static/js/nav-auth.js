const NAV_API_BASE = window.location.port === '5500' ? 'http://127.0.0.1:5000' : '';

document.addEventListener('DOMContentLoaded', () => {
  const loginLink = document.getElementById('navLoginLink');
  const logoutButton = document.getElementById('navLogoutButton');
  const rewardsLink = document.getElementById('navRewardsLink');

  let isAuthenticated = false;

  const updateAuthUI = () => {
    if (!loginLink || !logoutButton) return;
    if (isAuthenticated) {
      loginLink.style.display = 'none';
      logoutButton.hidden = false;
    } else {
      loginLink.style.display = '';
      logoutButton.hidden = true;
    }
  };

  const logout = async () => {
    try {
      await fetch(`${NAV_API_BASE}/logout`, {
        method: 'GET',
        credentials: 'include'
      });
      isAuthenticated = false;
      updateAuthUI();
    } catch (error) {
      console.error('Failed to logout:', error);
    }
  };

  const loadSession = async () => {
    try {
      const response = await fetch(`${NAV_API_BASE}/api/session`, {
        method: 'GET',
        credentials: 'include',
        headers: { 'Accept': 'application/json' }
      });
      if (response.ok) {
        const data = await response.json();
        isAuthenticated = !!data.authenticated;
        updateAuthUI();
      }
    } catch (error) {
      console.error('Failed to load session info:', error);
    }
  };

  if (logoutButton) {
    logoutButton.addEventListener('click', logout);
  }

  if (rewardsLink) {
    rewardsLink.addEventListener('click', (event) => {
      if (!isAuthenticated) {
        event.preventDefault();
        alert('Please log in to access rewards.');
        window.location.href = 'login.html?next=rewards.html';
      }
    });
  }

  loadSession();
});


