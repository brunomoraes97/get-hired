function getToken(){
  return document.cookie.split('; ').find(r => r.startsWith('token='));
}

function updateNav(){
  const logged = !!getToken();
  const login = document.getElementById('account-login');
  const register = document.getElementById('account-register');
  const profile = document.getElementById('account-profile');
  const logout = document.getElementById('account-logout');
  if(logged){
    if(login) login.style.display = 'none';
    if(register) register.style.display = 'none';
    if(profile) profile.style.display = 'block';
    if(logout) logout.style.display = 'block';
  } else {
    if(login) login.style.display = 'block';
    if(register) register.style.display = 'block';
    if(profile) profile.style.display = 'none';
    if(logout) logout.style.display = 'none';
  }
}

function setupLogout(){
  const logout = document.getElementById('account-logout');
  if(logout){
    logout.addEventListener('click', async (e) => {
      e.preventDefault();
      await fetch('/auth/logout', {method: 'POST'});
      document.cookie = 'token=; Max-Age=0; path=/';
      window.location.href = '/auth/logout';
    });
  }
}

function setupDropdown(){
  const btn = document.getElementById('nav-account-btn');
  const menu = document.getElementById('account-menu');
  if(btn && menu){
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      menu.classList.toggle('hidden');
    });
    document.addEventListener('click', (e) => {
      if(!btn.contains(e.target) && !menu.contains(e.target)){
        menu.classList.add('hidden');
      }
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  updateNav();
  setupLogout();
  setupDropdown();
});
