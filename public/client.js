// client-side js
// run by the browser each time your view template is loaded

// by default, you've got jQuery,
// add other scripts at the bottom of index.html

$(function() {
  let fbUsers;
  
  const authData = {"token": $('#user-token').text(), "url": $('#site-url').text(), "protocol": $('#site-protocol').text()};
    
  $.post('/siteData', authData, function(response) {
    fbUsers = response['users'];
    let siteData = response['siteData'];
    displayEverything(authData, siteData);
  });
  
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
    
  function displayEverything(token, siteData) {
      
    // in Knockout/MVVM,
    // * `shares` is model
    // * `viewModel` is viewModel
    // * <div id='shares-list'> is view

    var viewModel = {
      ufgUser: window.ko.observable('CHECKING'),
      editingUfg: window.ko.observable(false),
      changeUfg: function() {viewModel.editingUfg(true);},
      shouldShowShares: function() {return !viewModel.editingUfg() && validToken(viewModel);},
      shouldShowTokenEntry: function() {return viewModel.editingUfg();},
      updateToken: function() {
        viewModel.editingUfg(false);
        viewModel.ufgUser('CHECKING');
        token['ufgToken'] = viewModel.token();
        $.post('/updateToken', token, function(data) {
          const ixPerson = data['ixPerson'];
          if (ixPerson == -1) {
            viewModel.ufgUser("INVALID TOKEN")
          }
          else {
            const userName = lookupUser(ixPerson);
            viewModel.ufgUser(userName);  
          }
        });

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
        const data = {token: token['token'], url: token['url'], ufg_token: viewModel.token(), protocol: token['protocol'], data: JSON.stringify(dataList)}
        viewModel.disableSaveButton();

        $.post('/updateShares', data)
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
        
  }
  
});
