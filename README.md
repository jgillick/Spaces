# Spaces

A lightweight, intuitive, wiki-like knowledge base system that works.

A knowledge base should be a place that is effortless to update and always
provides the most relevant information at your fingertips. Unfortunately, the most
popular systems out there today are either complicated and force you to learn
a new syntax for writing, or easily get bogged down with outdated documentation.

This project's goal is to create a lightweight system that is easy to use
and *just works* in the ways you would want it to.

This is a work in progress, so check back soon.

## Goals

 * Easy & intuitive for everyone -- not just developers.
 * Able to create separate searchable content areas (i.e. Engineering, Design, Product).
 * Search that works.
 * Automatically flag out-of-date content and promote recent or popular content.
 * Customizable.

## What does wiki*-like* mean?

This is a wiki-like system, in that anyone with access should be able to create
new documents and edit existing ones. Where this differs is that it does not rely
on any wiki markup to write the documentation. Just simple, WYSIWYG tools that
let you type as if you were in your favorite word processor.

Plus instead of a flat system of documents, this can have hierarchy and separate
isolated areas.

## Why is it called Spaces?

The name comes from a primary goal of being able to create separate content areas, or spaces.
For example, your company might have the following spaces: Engineering, Design, Product, HR.
Under each space you can have full hierarchies of documents, organized any way you like.
Then users can search under specific space for the content they need.

## Framework

This is built as a Django site and should be able to be run directly (if you have
django and mysql installed). The end goal is to have the functionality extracted into
a python library that can be included in any existing django site.

## Install and run locally with Vagrant

Install Vagrant, and then run these steps:

```sh
vagrant up

vagrant ssh

runserver
```

Now open your browser to: http://localhost:8000/

**NOTE** If you get an error about port `8000` already being used, change the
port config value in `vagrant_config.rb` to something that is free.