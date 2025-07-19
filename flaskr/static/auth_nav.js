function getToken(){
  return document.cookie.split('; ').find(r => r.startsWith('token='));
}

function updateNav(){
  const logged = !!getToken();
  const login = document.getElementById('nav-account');
  const profile = document.getElementById('nav-profile');
  const logout = document.getElementById('nav-logout');
  if(logged){
    if(login) login.style.display = 'none';
    if(profile) profile.style.display = 'inline';
    if(logout) logout.style.display = 'inline';
  } else {
    if(login) login.style.display = 'inline';
    if(profile) profile.style.display = 'none';
    if(logout) logout.style.display = 'none';
  }
}

function setupLogout(){
  const logout = document.getElementById('nav-logout');
  if(logout){
    logout.addEventListener('click', async (e) => {
      e.preventDefault();
      await fetch('/auth/logout', {method: 'POST'});
      document.cookie = 'token=; Max-Age=0; path=/';
      window.location.href = '/auth/logout';
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  updateNav();
  setupLogout();
});
