class ResponseUtilities:
    """
        This provides the global response attributes

        How to use:
            1. Just inherit the class and work with the attributes
            2. use get_generated_response at last to get the generated response

        Customization:
            If you need to add more attributes or things in the response
            Simply override the get_generated_response and do just like you override other Class Based Views methods.
    """
    success_status:bool = False # This will be send as the indicator if the reqeust has success end or not
    message_to_client = None # This will have messages like ERROR message or SUCCESS message
    response_data = None # This will be the Response Data

    def get_generated_response(self):
        """
            Only adding the attribute that is available and returning     
        """
        generated_response = {
            "success_status" : self.success_status
        }

        if self.message_to_client:
            generated_response["message_from_server"] = self.message_to_client

        if self.response_data:
            generated_response["response_data"] = self.response_data

        import time
        time.sleep(2)
        return generated_response