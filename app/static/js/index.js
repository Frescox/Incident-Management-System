document.addEventListener("DOMContentLoaded", function () {
  // Referencias a elementos DOM
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const otpForm = document.getElementById("otp-form");
  const backButton = document.getElementById("back-to-form");
  const errorMessage = document.getElementById("error-message");
  const successMessage = document.getElementById("success-message");
  const verificacionContainer = document.getElementById("otp-verification");
  const authTabsContent = document.getElementById("authTabsContent");
  const telefonoContainer = document.getElementById("telefono-container");
  const metodoSMS = document.getElementById("metodo-sms");
  const metodoEmail = document.getElementById("metodo-email");

  // Mostrar/ocultar el campo de teléfono según el método de verificación
  metodoSMS.addEventListener("change", function () {
    if (this.checked) {
      telefonoContainer.style.display = "block";
      document
        .getElementById("reg-telefono")
        .setAttribute("required", "required");
    }
  });

  metodoEmail.addEventListener("change", function () {
    if (this.checked) {
      telefonoContainer.style.display = "none";
      document.getElementById("reg-telefono").removeAttribute("required");
    }
  });

  // Función para mostrar mensajes de error
  function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = "block";
    successMessage.style.display = "none";

    // Ocultar después de 5 segundos
    setTimeout(() => {
      errorMessage.style.display = "none";
    }, 5000);
  }

  // Función para mostrar mensajes de éxito
  function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.style.display = "block";
    errorMessage.style.display = "none";

    // Ocultar después de 5 segundos
    setTimeout(() => {
      successMessage.style.display = "none";
    }, 5000);
  }

  // Función para mostrar el panel de verificación OTP
function showVerificationPanel() {
  authTabsContent.style.display = "none";
  verificacionContainer.style.display = "block";
  setTimeout(() => {
    verificacionContainer.classList.add("show");
  }, 10);
}

  // Función para volver al formulario principal
function showMainPanel() {
  verificacionContainer.classList.remove("show");
  setTimeout(() => {
    verificacionContainer.style.display = "none";
    authTabsContent.style.display = "block";
  }, 300);
}

  // Evento para volver al formulario principal
  backButton.addEventListener("click", showMainPanel);

  // Manejar el envío del formulario de registro
  registerForm.addEventListener("submit", function (e) {
    e.preventDefault();

    // Validar que si se seleccionó SMS, se haya proporcionado un teléfono
    if (metodoSMS.checked && !document.getElementById("reg-telefono").value) {
      showError(
        "Por favor ingresa tu número de teléfono para verificación por SMS"
      );
      return;
    }

    // Recopilar datos del formulario
    const formData = new FormData(this);

    // Enviar solicitud al servidor
    fetch("/register", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showSuccess(data.message);
          if (data.show_otp_verification) {
            showVerificationPanel();
          }
          if (data.redirect) {
            setTimeout(() => {
              window.location.href = data.redirect;
            }, 2000);
          }
        } else {
          showError(data.message);
        }
      })
      .catch((error) => {
        showError(
          "Error al procesar tu solicitud. Inténtalo de nuevo más tarde."
        );
        console.error("Error:", error);
      });
  });

  // Manejar el envío del formulario de inicio de sesión
  loginForm.addEventListener("submit", function (e) {
    e.preventDefault();

    // Recopilar datos del formulario
    const formData = new FormData(this);

    // Enviar solicitud al servidor
    fetch("/login", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showSuccess(data.message);
          if (data.show_otp_verification) {
            showVerificationPanel();
          }
          if (data.redirect) {
            setTimeout(() => {
              window.location.href = data.redirect;
            }, 2000);
          }
        } else {
          showError(data.message);
        }
      })
      .catch((error) => {
        showError(
          "Error al procesar tu solicitud. Inténtalo de nuevo más tarde."
        );
        console.error("Error:", error);
      });
  });

  // Manejar el envío del formulario de verificación OTP
  otpForm.addEventListener("submit", function (e) {
    e.preventDefault();

    // Recopilar datos del formulario
    const formData = new FormData(this);

    // Enviar solicitud al servidor
    fetch("/verify_otp", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showSuccess(data.message);
          if (data.redirect) {
            setTimeout(() => {
              window.location.href = data.redirect;
            }, 2000);
          }
        } else {
          showError(data.message);
        }
      })
      .catch((error) => {
        showError(
          "Error al procesar tu solicitud. Inténtalo de nuevo más tarde."
        );
        console.error("Error:", error);
      });
  });
});