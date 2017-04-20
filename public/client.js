// client-side js
// run by the browser each time your view template is loaded

// by default, you've got jQuery,
// add other scripts at the bottom of index.html

$(function() {
  let fbUsers;

  function dropdownOfUsers() {
    let html = '<select name="person"">';
    for (let i in fbUsers) {
      const name = fbUsers[i].name;
      const ixPerson = fbUsers[i].ixPerson;
      html += '<option value="' + ixPerson + '">' + name + '</option>';
    }
    html += '</select>';
    return html;
  }
  
  const $tokenEntryButton = $("#token-entry button");
  $tokenEntryButton.on('click', tokenEntryButtonHandler);
  
  const $tokenEntryInput = $("#token-entry input");
  $tokenEntryInput.on('keyup', function(e) {
    if (e.keyCode == 13) {
      tokenEntryButtonHandler();
    }
  });
  $tokenEntryInput.focus();
  
  function tokenEntryButtonHandler() {
    $tokenEntryButton.prop('disabled', true);
    const token = {"token": $('#token-entry input').val()};
    
    $.getJSON('/fogbugzUsers', token, function(users) {
      fbUsers = users;
    })
      .done(function() {
        displayEverything(token);
      })
      .fail(function (jqXHR, error) {
        alert('Invalid token');
        $tokenEntryButton.prop('disabled', false);
      });

  }
  
  function displayEverything(token) {
    $('#token-entry').hide();
    $('#add-user').show();
    $('#form-div').show();
    $.getJSON('/userShares', token, function(shares) {
      for (const i in shares) {
        const html = '<div class="user" style="display:table;">' + 
                        '<div style="display:table-cell">' + 
                          dropdownOfUsers() +
                        '</div>' + 
                        '<div style="display:table-cell">' +
                          '<input type="number" name="shares" style="width: 40px; position: relative; left: 10px;">' +
                        '</div>' +
                        '<div style="display:table-cell">' +
                          '<button type="button" style="position: relative; left: 15px;">Remove</button>' +
                        '</div>'
                      '</div>';
        const $userShare = $(html);
          
        const $dropdown = $userShare.find('[name="person"]');
        $dropdown.val(shares[i].ixPerson);
        $dropdown.on('change', showSaveButton)

        const $shares = $userShare.find('[name="shares"]');
        $shares.val(shares[i].shares);
        $shares.on('input', showSaveButton);
      
        const $removeButton = $userShare.find('button');
        $removeButton.on('click', removeButtonHandler);
        
        const $sharesList = $('#shares-list');
        $sharesList.append($userShare);
      
      }
    });
  
    function removeButtonHandler() {
      const $button = $(this);
      const $mainElement = $button.parents('#shares-list div');
      $mainElement.remove();
      showSaveButton();
    }
  
    function showSaveButton() {
      $("#save-button").prop('disabled', false).show();
    }
  
    $("#add-user").on("click", function () {
      const html = '<div class="user" style="display:table;">' + 
                        '<div style="display:table-cell">' + 
                          dropdownOfUsers() +
                        '</div>' + 
                        '<div style="display:table-cell">' +
                          '<input type="number" name="shares" style="width: 40px; position: relative; left: 10px;">' +
                        '</div>' +
                        '<div style="display:table-cell">' +
                          '<button type="button" style="position: relative; left: 15px;">Remove</button>' +
                        '</div>'
                      '</div>';
    
      const $newUserShare = $(html);
      const $shares = $newUserShare.find('[name="shares"]');
      $shares.val(0);
          
      const $removeButton = $newUserShare.find('button');
      $removeButton.on('click', removeButtonHandler);
    
      const $dropdown = $newUserShare.find('[name="person"]');
      $dropdown.val(null);
        
      const $sharesList = $('#shares-list');
      $sharesList.append($newUserShare);
        
      showSaveButton();
    });
  
    $("#save-button").on('click', function () {
      $(this).prop('disabled', true);
      const dataList = []
      const $users = $(".user");
      for (let i = 0; i < $users.length; ++i) {
        const $user = $($users[i]);
        const ixPerson = parseInt($user.find('[name="person"]').val());
        if (!ixPerson) {
          continue;
        }
        const sFullName = $user.find('[name="person"] option:selected').text();
        const shares = parseInt($user.find('[name="shares"]').val());
        dataList.push({
          "name": sFullName,
          "shares": shares,
          "ixPerson": ixPerson
        });
      }
          
      const data = {token: token['token'], data: dataList}
    
      $.ajax({
        url: '/updateShares',
        type: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json; charset=utf-8'
      })
        .done(function() {
          $("#save-button").hide();
        })
        .fail(function(jqXHR, error) {
          alert(jqXHR.responseText);
          $('#save-button').prop('disabled', false);
        });
    });
        
  }
  
});
