FROM cirrusci/flutter:stable as build

WORKDIR /app

COPY pubspec.* ./

RUN flutter pub get

COPY . .

RUN flutter build apk --release

FROM alpine:latest

WORKDIR /app

COPY --from=build /app/build/app/outputs/flutter-apk/app-release.apk ./app.apk

RUN ls -lh ./app.apk
