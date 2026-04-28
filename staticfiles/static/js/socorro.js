function getCsrf(){return(document.cookie.split(';').find(c=>c.trim().startsWith('csrftoken='))||'').split('=')[1]||'';}
function showToast(msg,type='info'){const icons={success:'✅',error:'❌',warning:'⚠️',info:'ℹ️'};let wrap=document.querySelector('.toast-wrap');if(!wrap){wrap=document.createElement('div');wrap.className='toast-wrap';document.body.appendChild(wrap);}const t=document.createElement('div');t.className=`toast ${type}`;t.innerHTML=`<span>${icons[type]||'ℹ️'}</span><span style="flex:1">${msg}</span><button onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;color:var(--text3);font-size:16px;">×</button>`;wrap.appendChild(t);setTimeout(()=>t.remove(),5000);}
document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('[data-confirm]').forEach(el=>el.addEventListener('submit',e=>{if(!confirm(el.dataset.confirm||'Tem a certeza?'))e.preventDefault();}));
  document.querySelectorAll('.modal-backdrop').forEach(bd=>bd.addEventListener('click',e=>{if(e.target===bd)bd.classList.remove('open');}));
  document.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelectorAll('.modal-backdrop.open').forEach(m=>m.classList.remove('open'));});
});
