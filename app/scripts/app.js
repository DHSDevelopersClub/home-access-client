/*
Copyright (c) 2015 The Polymer Project Authors. All rights reserved.
This code may only be used under the BSD style license found at http://polymer.github.io/LICENSE.txt
The complete set of authors may be found at http://polymer.github.io/AUTHORS.txt
The complete set of contributors may be found at http://polymer.github.io/CONTRIBUTORS.txt
Code distributed by Google as part of the polymer project is also
subject to an additional IP rights grant found at http://polymer.github.io/PATENTS.txt
*/

(function (document) {
  'use strict';

  // Grab a reference to our auto-binding template
  // and give it some initial binding values
  // Learn more about auto-binding templates at http://goo.gl/Dx1u2g
  var app = document.querySelector('#app');

  app.displayInstalledToast = function() {
    document.querySelector('#caching-complete').show();
  };

  // Listen for template bound event to know when bindings
  // have resolved and content has been stamped to the page
  app.addEventListener('template-bound', function() {
    console.log('Our app is ready to rock!');
  });

  // See https://github.com/Polymer/polymer/issues/1381
  window.addEventListener('WebComponentsReady', function() {
    document.querySelector('body').removeAttribute('unresolved');

    // Ensure the drawer is hidden on desktop/tablet
    var drawerPanel = document.querySelector('#paperDrawerPanel');
    drawerPanel.forceNarrow = true;
  });

  app.passwordIsWrong = false;

  app.loadGradeInfo = function() {
    if (localStorage[app.username]) {
      try {
        app.classrooms = GibberishAES.dec(localStorage[app.username], app.password);
        console.log("loaded from localStorage");
      }
      catch(e) {
          app.passwordIsWrong = true;
          console.log("wrong password");
      }
    }

    if (!app.passwordIsWrong) {
      sendPostRequest(app.username, app.password, function(response){
        if (response.status === "OK") {
          localStorage[app.username] = GibberishAES.enc(response, app.password);
          app.classrooms = response;
          console.log("loaded from server");
        }
        else {
          app.passwordIsWrong = true;
          app.password = '';
          console.log("wrong password");
        }

      });
    }
  };

  var sendPostRequest = function(username, password, callback) {
   gapi.client.homeaccessclient.login({
       "username": username,
       "password": password,
   }).execute(callback);
  };

})(document);

// TODO: Decide if we still want to suggest wrapping as it requires
// using webcomponents.min.js.
// wrap document so it plays nice with other libraries
// http://www.polymer-project.org/platform/shadow-dom.html#wrappers
// )(wrap(document));
