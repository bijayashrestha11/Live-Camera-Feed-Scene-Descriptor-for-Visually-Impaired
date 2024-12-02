import 'package:cammelive/constants/text_styles.dart';
import 'package:flutter/material.dart';

Column titleSubTitleText(
  context, {
  required String title,
  required String subTitle,
  double subTitleWidth = 0.50,
  isMainTitle = true,
}) {
  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        title,
        style: isMainTitle
            ? headingStyle(weight: FontWeight.bold, color: Colors.black)
            : subHeadingStyle(weight: FontWeight.bold, color: Colors.black),
      ),
      SizedBox(
        width: MediaQuery.of(context).size.width * subTitleWidth,
        child: Text(subTitle,
            style: normalStyle(weight: FontWeight.normal, color: Colors.black)),
      )
    ],
  );
}
