import 'package:flutter/material.dart';

//push screen to stack and navigate to following Screen
navigateTo({required BuildContext context, required Widget screen, state}) {
  Navigator.push(
    context,
    MaterialPageRoute(builder: (BuildContext context) => screen),
  );
}

navigateAndRestore({required BuildContext context, required Widget screen}) {
  Navigator.of(context)
      .push(MaterialPageRoute(builder: (BuildContext context) => screen))
      .then((val) {});
}

//Replace previous screen from stack and set new screen as the previous stack
navigateToReplace({required BuildContext context, required Widget screen}) {
  Navigator.pushReplacement(
      context, MaterialPageRoute(builder: (BuildContext context) => screen));
}

//Remove all previous stack screen and set new screen as the first
navigateAndRemoveUntil(
    {required BuildContext context, required Widget screen}) {
  Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (context) => screen),
      (Route<dynamic> route) => false);
}

//go back to previous page
navigateBack({required BuildContext context}) {
  return Navigator.pop(context);
}
