// client-side js
// run by the browser each time your view template is loaded

// by default, you've got jQuery,
// add other scripts at the bottom of index.html

$(function() {
  let fbUsers;
  
  const $tokenEntryButton = $(".auth-button");
  $tokenEntryButton.on('click', tokenEntryButtonHandler);
  
  const $authInput = $(".authentication input");
  $authInput.on('keyup', function(e) {
    if (e.keyCode == 13) {
      tokenEntryButtonHandler();
    }
  });
  $authInput.focus();
  
  function tokenEntryButtonHandler() {
    $tokenEntryButton.prop('disabled', true);
    const data = {"token": $('.auth-token').val(), "url": $('.auth-url').val(), "protocol": $('.auth-url-protocol').val()};
    
    $.getJSON('/fogbugzUsers', data, function(users) {
      fbUsers = users;
    })
      .done(function() {
        displayEverything(data);
      })
      .fail(function (jqXHR, error) {
        if (jqXHR.status === 403) {
          alert('Invalid token');
          $tokenEntryButton.prop('disabled', false);
        }
        else if(jqXHR.status === 404) {
          promptForBotToken(data);
        }
      });

  }
  
  function promptForBotToken(data) {
    $('.authentication').hide();
    
  }
  
  function ObservableShare(share) {
    // creates an observable viewmodel for a "share"
    return {
      shares: window.ko.observable(share.shares),
      ixPerson: window.ko.observable(share.ixPerson)
    };
  }
  
  function sumShares() {
    var total = 0;
    var shares = this.shares(); // `this` is the ViewModel
    for (var ix = 0; ix < shares.length; ++ix){
      var user = shares[ix];
      total += parseInt(user.shares() || 0, 10);
    }
    return total;
  }
  
  function lookupUser(ixPerson) {
    for (let i = 0; i < fbUsers.length; i++) {
      if (fbUsers[i].ixPerson == ixPerson) {
        return fbUsers[i].name;
      }
    }
    return 'INVALID TOKEN';
  }
  
  function validToken(viewModel) {
    let validToken = viewModel.ufgUser() != 'CHECKING' && viewModel.ufgUser() != 'INVALID TOKEN';
    if (validToken) {
      $('#token-input').removeClass('invalid');
    } else {
      $('#token-input').addClass('invalid');
    }
    return validToken;
  }
    
  function displayEverything(token) {
    $('.authentication').hide();
    $('#form-div').show();
    $.getJSON('/userShares', token, function(siteData) {
      
      // in Knockout/MVVM,
      // * `shares` is model
      // * `viewModel` is viewModel
      // * <div id='shares-list'> is view
      
      var viewModel = {
        url: siteData['url'],
        uniqueID: siteData['unique_id'],
        ufgUser: window.ko.observable('CHECKING'),
        editingUfg: window.ko.observable(false),
        changeUfg: function() {viewModel.editingUfg(true);},
        shouldShowShares: function() {return !viewModel.editingUfg() && validToken(viewModel);},
        shouldShowTokenEntry: function() {return viewModel.editingUfg();},
        updateToken: function() {
          viewModel.editingUfg(false);
          viewModel.ufgUser('CHECKING');
          token['ufgToken'] = viewModel.token();
          $.ajax({
            url: '/updateToken',
            type: 'POST',
            data: JSON.stringify(token),
            contentType: 'application/json; charset=utf-8'
          })
            .done(function(data) {
              const ixPerson = data['ixPerson'];
              if (ixPerson == -1) {
                viewModel.ufgUser("INVALID TOKEN")
              }
              else {
                const userName = lookupUser(ixPerson);
                viewModel.ufgUser(userName);  
              }
            })

        },
        token: window.ko.observable(siteData['token']),
        shares: window.ko.observableArray(siteData['shares'].map(ObservableShare)),
        users: fbUsers,
        totalShares: sumShares,
        addUser: function() {
          let observableShare = ObservableShare({shares: 0, ixPerson: fbUsers[0].ixPerson});
          observableShare.shares.subscribe(viewModel.enableSaveButton);
          observableShare.ixPerson.subscribe(viewModel.enableSaveButton);
          viewModel.shares.push(observableShare);
        },
        removeUser: function() {
          viewModel.shares.remove(this);
        },
        save: function() {
          const dataList = viewModel.shares().map(share => ({shares: share.shares(), ixPerson: share.ixPerson()}));
          const data = {token: token['token'], url: token['url'], ufg_token: viewModel.token(), protocol: token['protocol'], data: dataList}
          viewModel.disableSaveButton();

          $.ajax({
            url: '/updateShares',
            type: 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json; charset=utf-8'
          })
            .fail(function(jqXHR, error) {
              alert(jqXHR.responseText);
              viewModel.enableSaveButton();
            });

        },
        enableSaveButton: function() {
          viewModel.saveButton(true);
        },
        disableSaveButton: function() {
          viewModel.saveButton(false);
        },
        saveButton: window.ko.observable(false)
      };
      
      viewModel.updateToken();
      viewModel.shares.subscribe(viewModel.enableSaveButton);
      let observableShares = viewModel.shares();
      $.each(observableShares, function(i) {
        observableShares[i].shares.subscribe(viewModel.enableSaveButton);
        observableShares[i].ixPerson.subscribe(viewModel.enableSaveButton);
      })
      
      window.ko.applyBindings(viewModel, document.getElementById('shares-page'));
      
    });
  
  }
  
});
