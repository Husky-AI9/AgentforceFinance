/**
* @File Name : HelloWorld.cls
* @Description :
* @Author :
* @Last Modified By :
* @Last Modified On : March 29, 2025
* @Modification Log :
*==============================================================================
* Ver | Date | Author | Modification
*==============================================================================
* 1.0 | March 29, 2025 |   | Initial Version
**/

public with sharing class SayHello {
    @InvocableMethod(label='Say Hello' description='Say Hello to the user')
    public static List<String> sayHello(List<String> name) {
        if (!String.isBlank(name[0])) {
            return new List<String>{ 'Hello ' + name[0] };
        } else {
            return new List<String>{ 'Error saying Hello. Input is missing' };
        }
    }
}