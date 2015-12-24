'use strict';

(function(){
  var generatedPath = '',
      titleField = $('form .title-field input'),
      pathField = $('form .path-field input');

  /**
    Checks if a path currently exists.
  */
  function pathExists(path) {
    $.GET(DOC_API + path)
    .then(
    function() {
      console.log('Exists!')
    },
    function() {
      console.log('Does not exist')
    });
  }

  /**
    Create a url slug for a string
  */
  function toSlug(value) {
    value = value.toLowerCase()
    value = value.replace(/[\s_]+/g, '-');      // Dashes
    value = value.replace(/[^a-z0-9\-]+/ig, ''); // Remove special chars

    // Remove extra dashes
    value = value.replace(/\-{2,}/g, '-');
    value = value.replace(/(^\-)|(\-$)/, '');

    return value;
  }

  /**
    Update URL path to be valid slugs
  */
  function updatePath(){
    var field = $('form .path-field input'),
        path = field.val(),
        pathSections;

    if (!path) {
      return;
    }

    // Convert path segments to slugs
    pathSections = path.split('/');
    pathSections.forEach(function(segment, i){
      pathSections[i] = toSlug(segment);
    });
    path = pathSections.join('/');

    field.val(path);
  }

  /**
    Convert title to a slug and add it to the path
  */
  function titleToPath() {
    var title = titleField.val(),
        initial = pathField[0].defaultValue,
        path = pathField.val(),
        slug;

    // Don't generate path if the user has already modified the path
    if (BASE_PATH != path.replace(/\/$/, '') && generatedPath != path) {
      return;
    }

    slug = toSlug(title);
    path = initial +'/'+ slug;
    path = path.replace(/\/{2,}/, '/'); // remove double slashes

    generatedPath = path;
    pathField.val(path);
  }

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

  /**
    Update path with title for a new document
  */
  if ($('.document-add').length) {
    pathField.change(function(){

    });
    titleField.keyup(function(){
      titleToPath();
    })
    .change(function(){
      titleToPath();
    })
    .blur(function(){
      titleToPath();
    });
  }

})();