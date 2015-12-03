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

 * Easy & intuitive to use by everyone (not just developers).
 * Able to create separate content areas (i.e. Engineering, Design, Product).
 * Search that works.
 * Automatically flag out-of-date content and promote recent or popular content.
 * Customizable.

## What does wiki-like mean?

This is a wiki-like system, in that anyone with access should be able to create 
new documents and edit existing ones. Where this differs is that it does not rely 
on any wiki markup to write the documentation. Just simple, WYSIWYG tools that 
let you type as if you were in your favorite word processor.

## Framework

This is built as a Django site and should be able to be run directly (if you have
django and mysql installed). The end goal is to have the functionality extracted into
a python library that can be included in any existing django site.

## Install and run locally with Vagrant

Install Vagrant, and then run these steps:

```sh
vagrant up

vagrant provision

vagrant ssh

python /vagrant/manage.py runserver 0.0.0.0:8000
```

Now open your browser to: http://localhost:8000/