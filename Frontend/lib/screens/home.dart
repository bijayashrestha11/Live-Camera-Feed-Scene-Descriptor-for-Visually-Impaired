import 'package:cammelive/constants/assets_path.dart';
import 'package:cammelive/constants/colors.dart';
import 'package:cammelive/constants/text_styles.dart';
import 'package:cammelive/screens/live_caption.dart';
import 'package:cammelive/screens/upload_video.dart';
import 'package:cammelive/utils/navigator.dart';
import 'package:cammelive/widgets/custom_button.dart';
import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: SafeArea(
        child: Stack(
          children: [
            // Illustration positioned at bottom right
            Positioned(
              right: 40,
              bottom: 160,
              child: Image.asset(
                AssetPath.backImg,
                height: MediaQuery.of(context).size.height * 0.42,
                fit: BoxFit.contain,
              ),
            ),
            // Main content
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 50),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 100),
                  Text(
                    'Real-time Vision,',
                    style: headingStyle(
                      weight: FontWeight.bold,
                      color: AppColor.secondaryColor,
                    ),
                  ),
                  Text(
                    'Powered by AI',
                    style: headingStyle(
                      weight: FontWeight.bold,
                      color: AppColor.secondaryColor,
                    ),
                  ),
                  const SizedBox(height: 20),
                  SizedBox(
                    width: MediaQuery.of(context).size.width * 0.55,
                    child: Text(
                      'Instantly caption your live surroundings to navigate the world with confidence',
                      style: subTitleStyle(
                        weight: FontWeight.w400,
                        color: AppColor.fadeTextColor,
                      ),
                    ),
                  ),
                  const SizedBox(height: 30),
                  customButton(
                    'Start Capturing',
                    width: 180,
                    height: 50,
                    onPress: () => navigateTo(
                      context: context,
                      screen: const P2PVideo(),
                    ),
                  ),
                  const Spacer(),
                  Text(
                    'Want to help?',
                    style: subTitleStyle(
                      weight: FontWeight.bold,
                      color: AppColor.secondaryColor,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Join our community of volunteers to improve our AI accuracy.',
                    style: normalStyle(
                      weight: FontWeight.w400,
                      color: AppColor.fadeTextColor,
                    ),
                  ),
                  const SizedBox(height: 8),
                  GestureDetector(
                    onTap: () => navigateTo(
                      context: context,
                      screen: const UploadVideoScreen(),
                    ),
                    child: Text(
                      'Learn More',
                      style: normalStyle(
                        weight: FontWeight.bold,
                        color: AppColor.secondaryColor,
                      ).copyWith(
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ),
                  const SizedBox(height: 40),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
