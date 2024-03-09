document.addEventListener('DOMContentLoaded', function() {
  // Add event listeners to buttons
  document.getElementById('createAccountBtnDriver').addEventListener('click', function() {
      // Redirect to create account page
      window.location.href = '/create_account/';
  });

  document.getElementById('createAccountBtnRider').addEventListener('click', function() {
    // Redirect to create account page
    window.location.href = '/create_account_rider/';
  });

  document.getElementById('loginBtn').addEventListener('click', function() {
      // Redirect to login page
      window.location.href = '/login_in/';
  });
});
