import 'package:cammelive/constants/colors.dart';
import 'package:cammelive/constants/text_styles.dart';
import 'package:flutter/material.dart';

Widget customButton(
  String text, {
  required Function() onPress,
  double width = 135,
  double height = 45,
}) {
  return SizedBox(
    width: width,
    height: height,
    child: ElevatedButton(
      onPressed: onPress,
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColor.primaryColor,
        shadowColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(40.0),
        ),
      ),
      child: Text(
        text,
        style:
            normalStyle(weight: FontWeight.w600, color: AppColor.secondaryColor)
                .copyWith(letterSpacing: 1),
      ),
    ),
  );
}
