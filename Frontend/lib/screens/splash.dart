import 'dart:async';

import 'package:cammelive/constants/colors.dart';
import 'package:cammelive/constants/text_styles.dart';
import 'package:cammelive/screens/home.dart';
import 'package:flutter/material.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({Key? key}) : super(key: key);

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    initializeApp(context);
    super.initState();
  }

  void initializeApp(context) {
    Timer(
      const Duration(seconds: 2),
      () {
        Navigator.popUntil(context, ModalRoute.withName('/screen'));
        Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const HomeScreen(),
            ));
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("CapMeLive",
                style: headingStyle(
                    weight: FontWeight.w900, color: AppColor.secondaryColor)),
            Text(
              "let us be your eyes",
              style: subTitleStyle(
                  weight: FontWeight.w400, color: AppColor.secondaryColor),
            )
          ],
        ),
      ),
    );
  }
}
