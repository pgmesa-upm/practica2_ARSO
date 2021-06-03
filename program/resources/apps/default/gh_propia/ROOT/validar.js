document.addEventListener('DOMContentLoaded', () => {
    let botAlta = document.getElementById('boton_alta');

    botAlta.onclick =  function validar() {
        
        let numero, letra, letras, formato, dni;
        letras = 'TRWAGMYFPDXBNJZSQVHLCKET';
        formato = /^\d{8}[a-zA-Z]$/;
        dni = document.forms["form_alta"]["DNI_ingresado"].value;
        if(formato.test(dni)){
            numero = dni.substr(0, dni.length-1);
            letra = dni.substr(dni.length-1, 1);
            numero = numero % 23;
            letras=letras.substring(numero, numero+1);
            if (letras!=letra) {
                alert("Letra errónea");
                return false;
            }
            else
            return true;
        } else {
            
            alert("Formato erróneo");
            return false;
        }
    }
})