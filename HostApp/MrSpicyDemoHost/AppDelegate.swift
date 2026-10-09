import UIKit

/// Host application for running the MrSpicyUI test suite inside a real
/// UIApplicationMain context (required for UIKit modal presentation and
/// UIControl event dispatch).
///
/// This is a component TEST HOST — it is not 8 Ball Pool and makes no claim
/// to be the production game. See validation/reports/integration-validation.md.
@main
final class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        let window = UIWindow(frame: UIScreen.main.bounds)
        let root = UIViewController()
        root.view.backgroundColor = .systemBackground
        window.rootViewController = root
        window.makeKeyAndVisible()
        self.window = window
        return true
    }
}
