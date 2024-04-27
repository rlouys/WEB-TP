/*******************************************************************
   SIDEBAR COLLAPSING
 *******************************************************************/

const toggler = document.querySelector(".btn");
toggler.addEventListener("click", function () {
    document.querySelector("#sidebar").classList.toggle("collapsed");
    this.classList.toggle('active');
});


/*******************************************************************
   REDIRECT MODIFY (FROM LISTE)
 *******************************************************************/

function redirectToModify(livreId, userId) {

    let url = '';

    if(livreId != null){
        url = `/modifier?id=${livreId}`;}
    else{
        url = `/modifier_user?id=${userId}`;}

    window.location.href = url; // Redirects the browser to the modify page
}


/*******************************************************************
   AJOUTER RANDOM LIVRES REQUIRES CONNEXION
 *******************************************************************/

function launchAlert() {
    Swal.fire({
        title: 'Authentication Required',
        text: "You need to be logged in to perform this action.",
        icon: 'error',
        showCancelButton: true,
        buttonsStyling: false,
        customClass: {
            confirmButton: 'btn btn-outline-danger',
            cancelButton: 'btn btn-outline-success',
        },
        confirmButtonText: 'Log in',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = '/connexion'; // Redirect to login page
        }
    });
}

/*******************************************************************
   CREATE RANDOM BOOKS
 *******************************************************************/

document.addEventListener("DOMContentLoaded", function() {
    const addButton10 = document.getElementById("add-random-books-10");
    const addButton100 = document.getElementById("add-random-books-100");

    // Function to handle adding books
    async function addBooks(bookCount) {
        console.log(`Button clicked to add ${bookCount} books`);

        try {
            const response = await fetch(`/generate_random_books?count=${bookCount}`);
            if (response.ok) {
                const data = await response.json();
                console.log("Books added successfully", data);

                // Optionally update the DOM with the new books
                // Redirect to /liste or refresh the page to show updated books
                console.log("Redirecting to /liste to show updated books.");
                window.location.href = '/liste'; // Redirect to the list page
            } else if (response.status === 401) {
                console.error("Authentication error");
                // Optionally handle authentication error more specifically
            } else {
                throw new Error(`Failed to fetch data from the server: ${response.status}`);
            }
        } catch (error) {
            console.error("Error:", error);
        }
    }

    // Event listeners for each button
    if (addButton10 != null && addButton100 != null) {
        addButton10.addEventListener("click", () => addBooks(10));
        addButton100.addEventListener("click", () => addBooks(100));
    }
});


/*******************************************************************
   CREATE RANDOM USERS
 *******************************************************************/


document.addEventListener("DOMContentLoaded", function() {
    const addButton5 = document.getElementById("add-random-users-5");
    const addButton50 = document.getElementById("add-random-users-50");

    // Function to handle adding users
    async function addUser(userCount) {
        console.log(`Button clicked to add ${userCount} users`);

        try {
            const response = await fetch(`/generate_random_user?count=${userCount}`);
            if (response.ok) {
                const data = await response.json();
                console.log("Users added successfully", data);

                // Optionally update the DOM with the new users
                // Redirect to /userlist or refresh the page to show updated users
                console.log("Redirecting to /userlist to show updated users.");
                window.location.href = '/userlist'; // Redirect to the list page
            } else if (response.status === 401) {
                console.error("Authentication error");
                // Optionally handle authentication error more specifically
            } else {
                throw new Error(`Failed to fetch data from the server: ${response.status}`);
            }
        } catch (error) {
            console.error("Error:", error);
        }
    }

    // Event listeners for each button
    if (addButton5 != null && addButton50 != null) {
        addButton5.addEventListener("click", () => addUser(5));
        addButton50.addEventListener("click", () => addUser(50));
    }

});




/*******************************************************************
   SUPPRIMER UN LIVRE ( Affiche un message d'alerte SweetAlerts )
 *******************************************************************/
function confirmDeletion(livreID, userID) {
    Swal.fire({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        buttonsStyling: false,
        customClass: {
            confirmButton: 'del-btn btn btn-outline-danger',
            cancelButton: 'del-btn btn btn-outline-success',
        },
        confirmButtonText: 'Yes, delete it!',
    }).then((result) => {
        if (result.isConfirmed) {

            if(livreID != null){
                action = '/supprimer';
                value = livreID;
            }else{
                action = '/supprimer_user';
                value = userID;
            }
            var form = document.createElement('form');
            form.method = 'POST';
            form.action = action;

            var hiddenField = document.createElement('input');
            hiddenField.type = 'hidden';
            hiddenField.name = 'id';
            hiddenField.value = value;
            form.appendChild(hiddenField);

            document.body.appendChild(form);
            form.submit();

        }
    });
}

/*******************************************************************
   LOADER INFINITY
 *******************************************************************/

document.addEventListener("DOMContentLoaded", function() {
        var loaderContainer = document.createElement('div');
        loaderContainer.style.position = 'fixed';
        loaderContainer.style.left = '0';
        loaderContainer.style.top = '0';
        loaderContainer.style.width = '100%';
        loaderContainer.style.height = '100%';
        loaderContainer.style.backgroundColor = 'rgba(241, 242, 243, 1)'; // Background color
        loaderContainer.style.zIndex = '9999';
        loaderContainer.style.display = 'flex';
        loaderContainer.style.justifyContent = 'center';
        loaderContainer.style.alignItems = 'center';

        // loader
        var loaderSVG = document.createElement('img');
        loaderSVG.src = '/static/src/Infinity-1s-200px.svg';
        loaderSVG.style.width = '200px'; 
        loaderSVG.style.height = '200px';

        loaderContainer.appendChild(loaderSVG);

        document.body.appendChild(loaderContainer);

        setTimeout(function() {
            document.body.removeChild(loaderContainer);
        }, 400); // La durée du loader en ms (ici 400 ms = 0.4s)
    });

/*******************************************************************
   CONSERVATION DU COOKIE DARKMODE / SIDEBAR MODE
 *******************************************************************/

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const sidebar = document.getElementById('sidebar');
    const sidebar2 = document.getElementById('sidebar2');
    const navbar = document.getElementById('navbar');
    const main = document.getElementById('main');
    const body = document.body;
    const footer = document.getElementById('footer');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const navBarToggleSwitch = document.getElementById('flexSwitchCheckChecked');
    const darkModeToggleSwitch = document.getElementById('flexSwitchCheckCheckedDark');
    const wrapper = document.querySelector('.wrapper.header'); // permet de corriger l'arrière plan de la sidebar (à cause du radius)
    const askpass = document.getElementById('askpass'); // permet de colorer en blanc le "Forgot your password?"
    // Utility functions to manage cookies
    function setCookie(name, value, days) {
        var expires = "";
        if (days) {
            var date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "") + expires + "; path=/; SameSite=Lax";
    }

    function getCookie(name) {
        var nameEQ = name + "=";
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    function setDefaultCookieIfAbsent(name, defaultValue, days) {
        var cookie = getCookie(name);
        if (cookie === null) { // Cookie not set
            setCookie(name, defaultValue, days);
        }
    }

    setDefaultCookieIfAbsent('darkmode', 'false', 1);
    setDefaultCookieIfAbsent('navmode', 'false', 1); // Assuming you also want a default for the navbar



    /************************************
      TOGGLE SIDEBAR MODE
     ************************************/
    function toggleNavBar(showNavBar) {
        if (showNavBar) {
            sidebar.style.display = 'none';
            sidebar2.style.display='none';
            navbar.style.display = 'block';

        } else {
            sidebar.style.display = 'block';
            sidebar2.style.display= 'block';
            navbar.style.display = 'none';
        }
        // Update the nav mode preference in the cookie
        setCookie('navmode', showNavBar, 1); // Save preference for 1 day
    }

    /************************************
      TOGGLE LIGHT/DARK MODE
     ************************************/
    function toggleDarkMode(isDarkMode) {
        if (isDarkMode) {
            main.classList.add('main-darkmode');
            body.classList.add('darkmode');
            footer.classList.add('footer-darkmode');
            sidebar.classList.add('sidebar-darkmode');
            sidebarToggle.setAttribute('data-bs-theme', 'dark');
            navbar.classList.remove('navbar-light', 'bg-light');
            sidebar2.style.backgroundColor = '#172A46';
            wrapper.classList.add('wrapper-darkmode');

            if (askpass) {
                askpass.style.color = 'rgba(255,255,255, 1)';
            }

        } else {
            main.classList.remove('main-darkmode');
            navbar.classList.remove('navbar-darkmode');
            body.classList.remove('darkmode');
            footer.classList.remove('footer-darkmode');
            sidebar.classList.remove('sidebar-darkmode');
            sidebarToggle.removeAttribute('data-bs-theme', 'dark');
            sidebar2.style.backgroundColor = '#FFFFFF';
            wrapper.classList.remove('wrapper-darkmode');
        }
        // Update the dark mode preference in the cookie
        setCookie('darkmode', isDarkMode, 1); // Save preference for 1 day
    }


    // Check the saved preferences and apply them
    var darkModePreference = getCookie('darkmode') === 'true';
    var navBarPreference = getCookie('navmode') === 'true';

    toggleNavBar(navBarPreference);
    toggleDarkMode(darkModePreference);
    navBarToggleSwitch.checked = navBarPreference;
    darkModeToggleSwitch.checked = darkModePreference;

    // Event listeners for toggle switches
    navBarToggleSwitch.addEventListener('change', function() {
        toggleNavBar(this.checked);
    });

    darkModeToggleSwitch.addEventListener('change', function() {
        toggleDarkMode(this.checked);
    });
});
// get out of dropdown clicking outside
document.addEventListener('click', function (event) {
    var openDropdown = document.querySelector('.dropdown-menu.show');
    if (openDropdown && !openDropdown.contains(event.target) && !event.target.matches('.dropdown-toggle')) {
        // Close the open dropdown if the click is outside
        openDropdown.classList.remove('show');
    }
});


/*******************************************************************
   VALIDATION ASYNCHRONE DU NOM D'UTILISATEUR ET DU MAIL
 *******************************************************************/
document.addEventListener('DOMContentLoaded', function() {
    const submitBtn = document.getElementById('submit-button');
    const usernameInput = document.getElementById('username');
    const usernameError = document.getElementById('usernameError');
    const emailInput = document.getElementById('email');
    const emailError = document.getElementById('emailError');

    let originalUsername = '';
    let originalEmail = '';
    if(usernameInput != null && emailInput != null)
    {
        originalUsername = usernameInput.value;
        originalEmail = emailInput.value;
    }

    // Fonction pour vérifier la validité du formulaire et activer/désactiver le bouton de soumission
    function checkFormValidity() {
        if(usernameError != null && emailError != null){
            const isUsernameErrorVisible = usernameError.style.display === 'block';
            const isEmailErrorVisible = emailError.style.display === 'block';
            submitBtn.disabled = isUsernameErrorVisible || isEmailErrorVisible; // Désactive le bouton si une erreur est visible
        }
    }

    // Validation du nom d'utilisateur
    if (usernameInput != null) {
        usernameInput.addEventListener('input', function(e) {
            const newUsername = e.target.value;
            if (newUsername === originalUsername) {
                usernameError.style.display = 'none';
            } else {
                fetch(`/api/check-username?username=${encodeURIComponent(newUsername)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.is_unique) {
                            usernameError.style.display = 'none';
                        } else {
                            usernameError.style.display = 'block';
                            usernameError.innerText = "Nom d'utilisateur indisponible."; // Mettez à jour le message si nécessaire
                        }
                        checkFormValidity(); // Vérifie si le formulaire est valide
                    }).catch(error => {
                        console.error('Error during username validation:', error);
                    });
            }
        });
    }

    // Validation de l'email
    if (emailInput) {
        emailInput.addEventListener('input', function(e) {
            const newEmail = e.target.value;
            if (newEmail === originalEmail) {
                emailError.style.display = 'none';
            } else {
                fetch(`/api/check-email?email=${encodeURIComponent(newEmail)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.is_unique) {
                            emailError.style.display = 'none';
                        } else {
                            emailError.style.display = 'block';
                            emailError.innerText = "Cet email est déja utilisé.";
                        }
                        checkFormValidity(); // Vérifie si le formulaire est valide
                    }).catch(error => {
                        console.error('Error during email validation:', error);
                    });
            }
        });
    }

    // Appelez la fonction checkFormValidity au chargement de la page pour définir l'état initial du bouton
    checkFormValidity();
});
