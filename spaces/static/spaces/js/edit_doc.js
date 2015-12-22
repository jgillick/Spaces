'use strict';

/**
  Delete form confirmation
*/
$('#delete-document-form').submit(function(event){
  var message = 'Are you sure you want to delete this document?\n'+
                'This action cannot be undone.';
  if (!window.confirm(message)) {
    event.preventDefault();
  }
});