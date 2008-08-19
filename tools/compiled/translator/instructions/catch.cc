/*********************************************************************
 *
 * Copyright (C) 2008,  Simon Kagstrom
 *
 * Filename:      catch.cc
 * Author:        Simon Kagstrom <simon.kagstrom@gmail.com>
 * Description:   The special "catch" instruction for try/catch pairs
 *
 * $Id:$
 *
 ********************************************************************/
class CatchInsn : public Instruction
{
public:
  CatchInsn(uint32_t address, int32_t extra) : Instruction(address, 0, R_ZERO, R_ZERO, R_ZERO, extra)
  {
    this->exception_classes = NULL;
    this->n_exception_classes = 0;
  }  

  bool pass1()
  {
    ElfSection *scn = elf->getSection(".cibylexceptionstrs");
    char *strs, *p;

    panic_if(!scn, "No .cibylexceptionsstr section found!");
    panic_if((size_t)this->extra > scn->size,
        "Offset %d outside of .cibylexceptionsstr section!", this->extra);
    strs = strdup((const char*)(scn->data + this->extra));

    /* Get all exception classes */
#define DELIMS " ,"
    p = strtok(strs, DELIMS);
    panic_if(!p, "Could not tokenize %s", strs);

    while ( p )
      {
        int cur = this->n_exception_classes;

        this->n_exception_classes++;
        this->exception_classes = (char**)xrealloc(this->exception_classes,
            sizeof(char*) * this->n_exception_classes);
        this->exception_classes[cur] = strdup(p); 
        p = strtok(NULL, DELIMS);
      }
#undef DELIMS

    free(strs);
    return true;
  }

  bool pass2()
  {
    JavaMethod *method = controller->getMethodByAddress(this->getAddress());
    Instruction *tryInstruction = controller->popTryStack();
    uint32_t start = tryInstruction->getAddress();
    uint32_t end = this->getAddress();
    const char *handler = method->addExceptionHandler(start, end);

    for ( int i = 0; i < this->n_exception_classes; i++ )
      emit->generic(".catch %s from L_%x to L_%x using %s\n",
          this->exception_classes[i], start, end, handler);  
    emit->bc_label(end);

    return true;
  }

  int getMaxStackHeight()
  {
    return 2;
  }

protected:
  char **exception_classes;
  int n_exception_classes;
};
