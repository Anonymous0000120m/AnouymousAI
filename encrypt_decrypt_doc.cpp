#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <filesystem>
#include <openssl/pem.h>
#include <openssl/rsa.h>
#include <openssl/err.h>
#include <openssl/x509.h>
#include <vector>
#include <iomanip>
#include <ctime>

namespace fs = std::filesystem;

void handleErrors() {
    ERR_print_errors_fp(stderr);
    abort();
}

void generateKeyPair(const std::string& privateKeyFile, const std::string& publicKeyFile) {
    RSA* rsa = RSA_generate_key(2048, RSA_F4, nullptr, nullptr);

    BIO* pbio = BIO_new_file(privateKeyFile.c_str(), "w+");
    PEM_write_bio_RSAPrivateKey(pbio, rsa, nullptr, nullptr, 0, nullptr, nullptr);
    BIO_free_all(pbio);

    BIO* pubio = BIO_new_file(publicKeyFile.c_str(), "w+");
    PEM_write_bio_RSAPublicKey(pubio, rsa);
    BIO_free_all(pubio);

    RSA_free(rsa);
}

RSA* loadPrivateKey(const std::string& keyFile) {
    BIO* bio = BIO_new_file(keyFile.c_str(), "rb");
    RSA* rsa = PEM_read_bio_RSAPrivateKey(bio, nullptr, nullptr, nullptr);
    BIO_free(bio);
    return rsa;
}

RSA* loadPublicKey(const std::string& keyFile) {
    BIO* bio = BIO_new_file(keyFile.c_str(), "rb");
    RSA* rsa = PEM_read_bio_RSAPublicKey(bio, nullptr, nullptr, nullptr);
    BIO_free(bio);
    return rsa;
}

std::vector<unsigned char> encrypt(const std::string& data, RSA* publicKey) {
    std::vector<unsigned char> encrypted(RSA_size(publicKey));
    int result = RSA_public_encrypt(data.size(), reinterpret_cast<const unsigned char*>(data.c_str()),
                                    encrypted.data(), publicKey, RSA_PKCS1_OAEP_PADDING);
    if (result == -1) handleErrors();
    return encrypted;
}

std::string decrypt(const std::vector<unsigned char>& encryptedData, RSA* privateKey) {
    std::vector<unsigned char> decrypted(RSA_size(privateKey));
    int result = RSA_private_decrypt(encryptedData.size(), encryptedData.data(),
                                      decrypted.data(), privateKey, RSA_PKCS1_OAEP_PADDING);
    if (result == -1) handleErrors();
    return std::string(reinterpret_cast<char*>(decrypted.data()), result);
}

void encryptDocument(const fs::path& documentPath, RSA* publicKey) {
    std::ifstream docFile(documentPath, std::ios::binary);
    std::ostringstream ss;
    ss << docFile.rdbuf();
    std::string documentContent = ss.str();
    docFile.close();

    std::vector<unsigned char> encryptedContent = encrypt(documentContent, publicKey);
    fs::path encryptedFilePath = documentPath;
    encryptedFilePath += ".encrypted";

    std::ofstream encryptedFile(encryptedFilePath, std::ios::binary);
    encryptedFile.write(reinterpret_cast<char*>(encryptedContent.data()), encryptedContent.size());
    encryptedFile.close();

    std::cout << "Document encrypted: " << encryptedFilePath << std::endl;
}

void decryptDocument(const fs::path& encryptedDocumentPath, RSA* privateKey) {
    std::ifstream encryptedFile(encryptedDocumentPath, std::ios::binary);
    std::vector<unsigned char> encryptedContent((std::istreambuf_iterator<char>(encryptedFile)),
                                               std::istreambuf_iterator<char>());
    encryptedFile.close();

    std::string originalDocumentContent = decrypt(encryptedContent, privateKey);
    fs::path originalDocumentPath = encryptedDocumentPath;
    originalDocumentPath.replace_extension();

    std::ofstream decryptedFile(originalDocumentPath, std::ios::binary);
    decryptedFile.write(originalDocumentContent.c_str(), originalDocumentContent.size());
    decryptedFile.close();

    std::cout << "Document decrypted: " << originalDocumentPath << std::endl;
}

void processDocuments(const fs::path& directoryPath, const std::string& keyFile, const std::string& action) {
    RSA* key = (action == "encrypt") ? loadPublicKey(keyFile) : loadPrivateKey(keyFile);
    if (!key) {
        std::cerr << "Error loading key file." << std::endl;
        return;
    }

    for (const auto& entry : fs::directory_iterator(directoryPath)) {
        if (entry.is_regular_file()) {
            if (action == "encrypt" && (entry.path().extension() == ".doc" || entry.path().extension() == ".docx")) {
                encryptDocument(entry.path(), key);
            } else if (action == "decrypt" && entry.path().extension() == ".encrypted") {
                decryptDocument(entry.path(), key);
            }
        }
    }

    RSA_free(key);
}

int main(int argc, char* argv[]) {
    if (argc < 5) {
        std::cerr << "Usage: " << argv[0] << " <action: encrypt/decrypt> <directory> <key file> <log file>" << std::endl;
        return 1;
    }

    std::string action = argv[1];
    std::string directory = argv[2];
    std::string keyFile = argv[3];
    std::string logFile = argv[4];

    // Log operations to console (or you could implement to write to logFile)
    std::cout << "Starting " << action << " process." << std::endl;
    processDocuments(directory, keyFile, action);
    std::cout << action << " process completed." << std::endl;

    return 0;
}
