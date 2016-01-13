/**
 * @license Copyright (c) 2003-2015, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here.
	// For complete reference see:
	// http://docs.ckeditor.com/#!/api/CKEDITOR.config

	// The toolbar groups arrangement, optimized for two toolbar rows.
	config.toolbar = [
		{ name: 'styles', items: [ 'Format' ] },
		{ name: 'basicstyles', items: [ 'Bold', 'Italic', 'Strike', 'Code', 'RemoveFormat' ] },
		// { name: 'styles', items: [ 'Font', 'FontSize' ] },
		{ name: 'paragraph', items: [ 'NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CodeSnippet' ] },
		// '/',
		{ name: 'links', items: [ 'Link', 'Unlink', 'Anchor' ] },
		// { name: 'colors', items: [ 'TextColor', 'BGColor' ] },
		{ name: 'insert', items: [ 'Image', 'Table', 'HorizontalRule' ] },
		{ name: 'document', items: [ 'Source' ] },
		// { name: 'markdown', items: [ 'Markdown' ] }
	];


	// Remove some buttons provided by the standard plugins, which are
	// not needed in the Standard(s) toolbar.
	config.removeButtons = 'Underline,Subscript,Superscript';

	// Set the most common block elements.
	config.format_tags = 'p;h1;h2;h3;pre';

	// Simplify the dialog windows.
	config.removeDialogTabs = 'image:advanced;link:advanced';

	config.extraPlugins = 'dragresize,dropler'; //markdown

	// Drag/drop upload
	config.droplerConfig = {
    backend: 'basic',
    settings: {
    	uploadUrl: window.UPLOAD_URL
    }
  }
};
