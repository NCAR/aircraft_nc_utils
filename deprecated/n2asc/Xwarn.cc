/*
-------------------------------------------------------------------------
OBJECT NAME:	Xwarn.c

FULL NAME:	Show Warning Box with Message

DESCRIPTION:	CreateWarn should be called once where you initialize
		your X stuff.  To use just call WarnUser(ErrMsg, callBack)

INPUT:		String to Display.  Callback to call if user hits OK.

OUTPUT:		Warning message in its own tidy little window.

AUTHOR:		cjw@ucar.edu
-------------------------------------------------------------------------
*/

#include <cstdio>

#include <Xm/Xm.h>
#include <Xm/MessageB.h>

static const int nWarnings = 3;

static Widget	warnBox[nWarnings];
static int	inUse[nWarnings];

void CancelWarning(Widget, XtPointer, XtPointer);

/* -------------------------------------------------------------------- */
void WarnUser(const char str[], void (*okCB)(Widget, XtPointer, XtPointer), void (*cancelCB)(Widget, XtPointer, XtPointer))
{
  int		i;
  Widget	label;
  Arg		args[5];
  XmString	xStr;

  for (i = 0; i < nWarnings; ++i)
    if (inUse[i] == FALSE)
      break;

  if (i == nWarnings)
  {
    fprintf(stderr, "WarnUser: Out of warning boxes.\n");
    i = 0;
  }

  inUse[i] = TRUE;

  label = XmMessageBoxGetChild(warnBox[i], XmDIALOG_MESSAGE_LABEL);
  xStr = XmStringCreateLtoR((char *)str, XmSTRING_DEFAULT_CHARSET);
  XtSetArg(args[0], XmNlabelString, xStr);
  XtSetValues(label, args, 1);
  XmStringFree(xStr);

  XtRemoveAllCallbacks(warnBox[i], XmNokCallback);
  XtAddCallback(warnBox[i], XmNokCallback, CancelWarning, (XtPointer)i);

  XtRemoveAllCallbacks(warnBox[i], XmNcancelCallback);
  XtAddCallback(warnBox[i], XmNcancelCallback, CancelWarning, (XtPointer)i);

  if (okCB)
    XtAddCallback(warnBox[i], XmNokCallback, (XtCallbackProc)okCB, (XtPointer)i);
  if (cancelCB)
    XtAddCallback(warnBox[i], XmNcancelCallback, (XtCallbackProc)cancelCB, (XtPointer)i);

  XtManageChild(warnBox[i]);
  XtPopup(XtParent(warnBox[i]), XtGrabNonexclusive);

}	/* END WARNUSER */

/* -------------------------------------------------------------------- */
/* ARGSUSED */
void CancelWarning(Widget w, XtPointer clientData, XtPointer callData)
{
  XtUnmanageChild(warnBox[(long)clientData]);
  XtPopdown(XtParent(warnBox[(long)clientData]));
  inUse[(long)clientData] = FALSE;

}	/* END CANCELWARNING */

/* -------------------------------------------------------------------- */
void CreateWarningBox(Widget parent)
{
  for (int i = 0; i < nWarnings; ++i)
  {
    inUse[i] = FALSE;
    warnBox[i] = XmCreateWarningDialog(parent, (char *)"warnBox", NULL, 0);
    XtSetSensitive(XmMessageBoxGetChild(warnBox[i], XmDIALOG_HELP_BUTTON), FALSE);
  }

}	/* END CREATEWARNINGBOX */

/* END XWARN.C */
