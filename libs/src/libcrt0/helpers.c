/*********************************************************************
 *
 * Copyright (C) 2006,  Blekinge Institute of Technology
 *
 * Filename:      helpers.c
 * Author:        Simon Kagstrom <ska@bth.se>
 * Description:   C runtime helpers
 *
 * $Id: helpers.c 13852 2007-02-24 07:26:18Z ska $
 *
 ********************************************************************/
#include <stdio.h>
#include <cibyl.h>

#include <java/lang.h>

extern unsigned long __ctors_begin;
extern unsigned long __ctors_end;
extern unsigned long __dtors_begin;
extern unsigned long __dtors_end;

static void run_list(unsigned long *start, unsigned long *end)
{
  void (**p)(void) = (void (**)(void))start;

  while (p != (void (**)(void))end)
    {
      (*p)();
      p++;
    }
}

void crt0_run_global_constructors(void)
{
  run_list(&__ctors_begin, &__ctors_end);
}

void crt0_run_global_destructors(void)
{
  run_list(&__dtors_begin, &__dtors_end);
}

/* This is a quite common case for an exception handler */
void NOPH_setter_exception_handler(NOPH_Exception_t ex, void *arg)
{
  int *p = (int*)arg;
  *p = 1;

  NOPH_delete(ex);
}

/* Dummy functions - handled by builtins always */
void __NOPH_try(void (*callback)(NOPH_Exception_t exception, void *arg), void *arg)
{
}

void __NOPH_catch(void)
{
}

void __NOPH_throw(NOPH_Exception_t ex)
{
}
