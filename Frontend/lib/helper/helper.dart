import 'package:flutter/material.dart';

errorMessage(BuildContext context, message, {Color? color}) async {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      backgroundColor: color ?? Colors.red,
      content: Text(message),
    ),
  );
}
