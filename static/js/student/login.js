function showpass(){
    var x=document.getElementById("password");
    if (x.type==="password"){
        x.type="text";
        document.getElementById("password").classList.replace("fa-solid fa-eye-slash", "fa-solid fa-eye");
    }
    else{
        x.type="password";
    }
}