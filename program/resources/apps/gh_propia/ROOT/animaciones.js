
document.addEventListener('DOMContentLoaded', () => {
    let foto = document.getElementById('foto_alumno');
    let p1 = document.getElementById('p1');
    
    foto.onclick = function (){
        foto.setAttribute('src', "Mis_archivos_web/imagen3.png");
        p1.textContent = "Imagen 3 (Triste)";
    }
    foto.onmouseover = function (){
        foto.setAttribute('src', "Mis_archivos_web/imagen2.png");
        p1.textContent = "Imagen 2 (Sonriente)";
    }
    
    foto.onmouseout = function (){
        foto.setAttribute('src', "Mis_archivos_web/imagen1.png");
        p1.textContent = "Imagen 1 (Enfadado)";
    }
})
