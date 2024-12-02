import 'package:flutter/material.dart';

TextStyle myTextStyle(double fontSize, String fontFamily, FontWeight fontWeight,
    Color color, TextDecoration decoration) {
  return TextStyle(
      fontSize: fontSize,
      fontWeight: fontWeight,
      fontFamily: fontFamily,
      color: color,
      decoration: decoration);
}

TextStyle headingStyle({
  required FontWeight weight,
  required Color color,
}) {
  return myTextStyle(38, "Poppins", weight, color, TextDecoration.none);
}

TextStyle subHeadingStyle({
  required FontWeight weight,
  required Color color,
}) {
  return myTextStyle(30, "Poppins", weight, color, TextDecoration.none);
}

TextStyle subTitleStyle({
  required FontWeight weight,
  required Color color,
}) {
  return myTextStyle(16, "Poppins", weight, color, TextDecoration.none);
}

TextStyle normalStyle({
  required FontWeight weight,
  required Color color,
}) {
  return myTextStyle(14, "Poppins", weight, color, TextDecoration.none);
}

TextStyle subNormalStyle({
  required FontWeight weight,
  required Color color,
}) {
  return myTextStyle(10, "Poppins", weight, color, TextDecoration.none);
}
